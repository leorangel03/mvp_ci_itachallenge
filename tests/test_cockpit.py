import pandas as pd
import pytest

from src.cockpit import backtest, clube, decisoes, jornada, motor, seguranca
from src.cockpit.dados import INDISPONIVEL, carregar_base


@pytest.fixture(scope="module")
def base():
    return carregar_base()


@pytest.fixture(scope="module")
def previsao():
    from src.models.forecast_demanda import PrevisaoDemanda
    from src.cockpit.dados import ROOT
    path = ROOT / "data" / "processed" / "forecast_demanda.csv"
    return pd.read_csv(path) if path.exists() else PrevisaoDemanda(ROOT).build()


@pytest.fixture(scope="module")
def decisoes_df(base, previsao):
    return motor.calcular_decisoes(base, previsao, jornada.jornada_parceiros(base))


def test_seis_verificacoes_de_seguranca_passam(base, previsao):
    r = seguranca.executar(base, previsao)
    assert len(r) == 6
    assert r["passou"].all(), r[~r["passou"]].to_dict("records")


def test_ci0004_prioriza_producao_com_falta_de_563(decisoes_df):
    r = decisoes_df.set_index("sku").loc["CI-0004"]
    assert r["recomendacao"] == "Priorizar produção"
    assert r["carteira"] == 866 and r["estoque"] == 303
    assert "563" in r["motivo"]
    assert r["producao_sugerida"] % r["lote_minimo"] == 0


def test_ci0031_reduz_op_que_cobre_15_meses(decisoes_df):
    r = decisoes_df.set_index("sku").loc["CI-0031"]
    assert r["recomendacao"] == "Reduzir/adiar OP"
    assert r["meses_cobertos_maior_op"] == pytest.approx(15.3, abs=0.2)


def test_pedidos_em_risco_e_excesso(base):
    risco = motor.pedidos_em_risco(base)
    assert int(risco["em_risco"].sum()) == 23
    assert risco.loc[risco["em_risco"], "valor"].sum() == pytest.approx(641796, abs=1)
    ex = motor.excesso_resumo(base)
    assert ex["atual"] == pytest.approx(226376, abs=1) and ex["com_ops"] == pytest.approx(681297, abs=1)


def test_jornada_ponto_cego_e_ka02(base):
    cob = jornada.cobertura_consumo(base).set_index("recorte")["participacao"]
    assert cob["KAs sem sell-out"] == pytest.approx(24.9, abs=0.1)
    res = jornada.resumo_parceiros(jornada.jornada_parceiros(base), base)
    assert res["sell_in_sobre_sell_out"].idxmax() == "KA-02"
    jp = jornada.jornada_parceiros(base)
    assert jp.loc[~jp["tem_sell_out"], "sell_out_12m"].isna().all()  # ausência nunca vira zero
    assert set(jp.loc[~jp["tem_sell_out"], "natureza"]) <= {INDISPONIVEL, "Estimado"}


def test_backtest_reproduz_semana_2(base):
    bt = backtest.rodar_backtest(base["Vendas_24m"], base["Produtos"])
    res = backtest.resumo(bt)
    assert res.index[0] == "sazonal_familia_nivel_sku"
    assert res.loc["sazonal_familia_nivel_sku", "wape"] == pytest.approx(9.18, abs=0.01)
    assert res.loc["sazonal_ingenuo", "wape"] == pytest.approx(11.33, abs=0.01)
    assert (res["n_previsoes"] == 1650).all()
    h = backtest.holdout(bt)
    assert h.loc["sazonal_familia_nivel_sku", "wape_teste"] < h.loc["sazonal_ingenuo", "wape_teste"]


def test_registro_exige_responsavel_e_motivo(tmp_path):
    p = tmp_path / "log.csv"
    with pytest.raises(ValueError):
        decisoes.registrar_decisao("CI-0004", "Priorizar produção", 1000, "Rejeitar", 0, "PCP", "", path=p)
    with pytest.raises(ValueError):
        decisoes.registrar_decisao("CI-0004", "Priorizar produção", 1000, "Aprovar", 1000, " ", "", path=p)
    log = decisoes.registrar_decisao("CI-0004", "Priorizar produção", 1000, "Aprovar", 999, "PCP", "", path=p)
    assert log.iloc[-1]["quantidade_aprovada"] == 1000


def test_nf_valida_identifica_parceiro_e_bloqueia_reuso():
    chave = clube.gerar_chave_exemplo("22333444000172")
    r = clube.validar_compra(chave, "CI-0009", set())
    assert r.valida and r.parceiro == "KA-02" and r.natureza == "Verificado pelo consumidor"
    assert not clube.validar_compra(chave, "CI-0009", {chave}).valida
    errada = chave[:-1] + str((int(chave[-1]) + 1) % 10)
    assert not clube.validar_compra(errada, "CI-0009", set()).valida


def test_modelo_economico_cenario_base():
    sim = clube.simular(clube.CENARIOS["Base"])
    assert clube.payback(sim) == 9
    assert sim["acumulado"].iloc[-1] == pytest.approx(919530, abs=5)
