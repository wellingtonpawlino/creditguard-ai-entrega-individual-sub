"""
Diagrama de Arquitetura — CreditGuard AI
Estilo: arquitetura corporativa / consultoria
"""

import matplotlib
matplotlib.rcParams["font.family"] = "DejaVu Sans"

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── Setup ─────────────────────────────────────────────────────────────────────
W, H = 24, 17
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

# ── Paleta ────────────────────────────────────────────────────────────────────
DARK    = "#0D2137"
NAVY    = "#1A3A5C"
BLUE    = "#2563A8"
SKY     = "#3B82C4"
GREEN   = "#166534"
TEAL    = "#0E6655"
GRAY    = "#374151"
LGRAY   = "#6B7280"
PANEL   = "#F0F4F8"
PANEL2  = "#EAF4EC"
WHITE   = "#FFFFFF"
DIVIDER = "#CBD5E1"
AMBER   = "#92400E"
RED     = "#991B1B"
EMERALD = "#14532D"

# ── Helpers ───────────────────────────────────────────────────────────────────
def rbox(x, y, w, h, fc, ec=WHITE, lw=1.2, radius=0.25, zorder=3):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={radius}",
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder)
    ax.add_patch(p)


def txt(x, y, s, fs=9, color=WHITE, weight="bold",
        ha="center", va="center", zorder=5, alpha=1.0, style="normal"):
    ax.text(x, y, s, fontsize=fs, color=color, fontweight=weight,
            ha=ha, va=va, zorder=zorder, linespacing=1.4,
            alpha=alpha, fontstyle=style)


def arrow_v(x, y1, y2, color=DARK, lw=1.6, zorder=6):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=12), zorder=zorder)


def arrow_h(x1, x2, y, color=DARK, lw=1.6, zorder=6):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=12), zorder=zorder)


def tag(x, y, s, fc=BLUE, tc=WHITE, fs=7.0, zorder=7):
    ax.text(x, y, s, fontsize=fs, color=tc, ha="center", va="center",
            zorder=zorder, bbox=dict(boxstyle="round,pad=0.28", fc=fc, ec="none"))


# ══════════════════════════════════════════════════════════════════════════════
#  TITULO
# ══════════════════════════════════════════════════════════════════════════════
rbox(0.3, 15.8, W - 0.6, 1.0, fc=DARK, ec=DARK, radius=0.2, zorder=2)
txt(W / 2, 16.32, "Arquitetura End-to-End de Predicao de Inadimplencia",
    fs=14.5, color=WHITE)
txt(W / 2, 15.97, "CreditGuard AI  |  ProScore Analytics  |  Home Credit Default Risk  |  CRISP-DM",
    fs=8, color="#94A3B8", weight="normal")

# ══════════════════════════════════════════════════════════════════════════════
#  PAINEIS DE FUNDO
# ══════════════════════════════════════════════════════════════════════════════
rbox(0.3, 1.6, 10.9, 13.95, fc=PANEL, ec=DIVIDER, lw=1.0, radius=0.3, zorder=1)
txt(5.75, 15.35, "PIPELINE DE TREINAMENTO  |  OFFLINE",
    fs=8.5, color=NAVY)

rbox(13.0, 1.6, 10.7, 13.95, fc=PANEL2, ec=DIVIDER, lw=1.0, radius=0.3, zorder=1)
txt(18.35, 15.35, "PIPELINE DE INFERENCIA  |  ONLINE",
    fs=8.5, color=GREEN)

ax.plot([11.85, 11.85], [1.7, 15.6], color=DIVIDER, lw=1.5, ls="--", zorder=2)

# ══════════════════════════════════════════════════════════════════════════════
#  COLUNA ESQUERDA — TREINO
# ══════════════════════════════════════════════════════════════════════════════
LX, LW, LC = 0.72, 10.15, 5.795

# 1 — Data Sources
rbox(LX, 13.3, LW, 1.85, fc=NAVY, radius=0.2)
txt(LC, 14.45, "Home Credit Dataset", fs=10.5)
txt(LC, 14.1, "application_train.csv  |  307.511 linhas x 122 colunas", fs=8.5, weight="normal")
txt(LC, 13.77, "bureau.csv  |  1.716.428 linhas x 17 colunas", fs=8.5, weight="normal")
txt(LC, 13.46, "Kaggle — Home Credit Default Risk", fs=7.5, weight="normal", alpha=0.72)

arrow_v(LC, 13.3, 12.52, color=NAVY)

# 2 — DataPipeline
rbox(LX, 11.3, LW, 1.12, fc=BLUE, radius=0.2)
txt(LC, 12.0, "DataPipeline", fs=10.5)
txt(LC, 11.67, "data_sanitization.py  |  Feature Engineering  |  Agregacao Bureau", fs=8.2, weight="normal")
txt(LC, 11.4, "abt_transform.py  |  Validacao de Shape  (307.511 x 186)", fs=8.2, weight="normal")

arrow_v(LC, 11.3, 10.52, color=BLUE)
tag(LC + 1.6, 10.91, "8 features derivadas + 44 agregacoes bureau")

# 3 — ABT
rbox(LX, 9.28, LW, 1.14, fc=SKY, radius=0.2)
txt(LC, 9.97, "Analytical Base Table  (ABT)", fs=10.5)
txt(LC, 9.63, "307.511 clientes  |  185 features brutas  |  1 TARGET", fs=8.8, weight="normal")
txt(LC, 9.36, "91,93% adimplentes  |  8,07% inadimplentes  |  razao 11,4:1", fs=8, weight="normal")

arrow_v(LC, 9.28, 8.32, color=SKY)
tag(LC + 1.7, 8.8, "train_test_split  80/20  |  stratify=y  |  random_state=42")

# 4 — Model Training
rbox(LX, 6.65, LW, 1.57, fc=BLUE, radius=0.2)
txt(LC, 8.33, "Selecao de Modelos  |  5 Algoritmos Comparados", fs=10.5)

models = [
    ("Dummy",        LGRAY, "AUC 0.50"),
    ("Log. Reg.",    LGRAY, "AUC 0.67"),
    ("Random\nForest", SKY, "AUC 0.75"),
    ("XGBoost",      SKY,   "AUC 0.78"),
    ("LightGBM",   GREEN,   "AUC 0.78"),
]
mw = 1.82
for i, (name, fc, auc) in enumerate(models):
    mx = LX + 0.18 + i * (mw + 0.1)
    rbox(mx, 6.73, mw, 0.82, fc=fc, ec=WHITE, lw=0.8, radius=0.12, zorder=4)
    txt(mx + mw / 2, 7.15, name, fs=7.8)
    txt(mx + mw / 2, 6.85, auc, fs=6.8, weight="normal", alpha=0.88)

arrow_v(LC, 6.65, 5.78, color=GREEN)
tag(LC + 1.5, 6.21, "Selecionado por ROC-AUC maximo")

# 5 — LightGBM Winner
rbox(LX, 4.48, LW, 1.2, fc=GREEN, ec=EMERALD, lw=1.5, radius=0.2)
txt(LC, 5.33, "LightGBM  |  Modelo em Producao  (v3)", fs=11)
txt(LC, 4.98, "ROC-AUC  0,7778   |   Recall  65,82%   |   Precision  18,90%   |   F1  29,37%", fs=9, weight="normal")
txt(LC, 4.68, "class_weight='balanced'  |  num_leaves=31  |  n_estimators=700  |  Tempo: 7,2 s", fs=7.8, weight="normal")

arrow_v(LC, 4.48, 3.6, color=GREEN)

# 6 — Artefatos
rbox(LX, 2.25, LW, 1.25, fc=TEAL, radius=0.2)
txt(LC, 3.15, "Artefatos Serializados  (Model/artifacts/)", fs=10.5)
txt(LC, 2.82, "best_model.joblib   |   preprocessor.joblib   |   features.joblib  (185)", fs=8.5, weight="normal")
txt(LC, 2.54, "all_models.joblib   |   predictions_test.joblib   |   metadata_modelo.json", fs=8.2, weight="normal")
txt(LC, 2.32, "comparacao_modelos.csv", fs=7.5, weight="normal", alpha=0.75)

# ══════════════════════════════════════════════════════════════════════════════
#  BLOCO CENTRAL — MinIO
# ══════════════════════════════════════════════════════════════════════════════
rbox(10.95, 2.25, 2.85, 1.25, fc=DARK, ec="#374151", lw=1.2, radius=0.2, zorder=3)
txt(12.375, 3.22, "MinIO", fs=10, color=WHITE)
txt(12.375, 2.92, "Model Registry", fs=8, color="#94A3B8", weight="normal")
txt(12.375, 2.62, "model-artifacts/v3/", fs=7.2, color="#64748B", weight="normal")
txt(12.375, 2.4,  "API :9100  |  Console :9101", fs=6.8, color="#64748B", weight="normal", alpha=0.85)

arrow_h(LX + LW, 12.375, 2.875, color=TEAL)
tag(11.5, 2.875 + 0.22, "storage.py")

arrow_h(13.8, 13.45, 2.875, color=DARK)
tag(13.6, 2.875 + 0.22, "joblib.load()")

# ══════════════════════════════════════════════════════════════════════════════
#  COLUNA DIREITA — INFERENCIA
# ══════════════════════════════════════════════════════════════════════════════
RX, RW, RC = 13.25, 10.45, 18.475

# 1 — Usuario
rbox(RX, 13.3, RW, 1.0, fc=NAVY, radius=0.2)
txt(RC, 13.92, "Analista de Credito", fs=10.5)
txt(RC, 13.6, "Solicita avaliacao de risco via interface web", fs=8.5, weight="normal")

arrow_v(RC, 13.3, 12.52, color=NAVY)

# 2 — Streamlit
rbox(RX, 11.3, RW, 1.12, fc=BLUE, radius=0.2)
txt(RC, 12.0, "Streamlit Application  |  app/app.py", fs=10.5)
txt(RC, 11.67, "8 campos coletados  |  Sidebar com metricas dinamicas", fs=8.2, weight="normal")
txt(RC, 11.4, "MODEL_VERSION=v3  |  Porta 8501  |  @st.cache_resource", fs=8, weight="normal")

arrow_v(RC, 11.3, 10.52, color=BLUE)

# 3 — predict.py
rbox(RX, 9.28, RW, 1.14, fc=SKY, radius=0.2)
txt(RC, 9.97, "Model/predict.py", fs=10.5)
txt(RC, 9.63, "_enrich_input()  |  Feature Engineering Online  |  185 features", fs=8.5, weight="normal")
txt(RC, 9.36, "Replica identicamente create_application_features() do DataPipeline", fs=8, weight="normal")

arrow_v(RC, 9.28, 8.32, color=SKY)
tag(RC + 1.3, 8.8, "DataFrame  (1 x 185)")

# 4 — ColumnTransformer
rbox(RX, 6.65, RW, 1.57, fc=BLUE, radius=0.2)
txt(RC, 8.33, "ColumnTransformer  |  preprocessor.joblib", fs=10.5)
txt(RC, 7.98, "Fitted exclusivamente em X_train  |  Sem data leakage", fs=8.2, weight="normal")

rbox(RX + 0.25, 6.73, 4.8, 0.72, fc=SKY, ec=WHITE, lw=0.8, radius=0.12, zorder=4)
txt(RX + 2.65, 7.09, "169 numericas  |  SimpleImputer (median)", fs=8)

rbox(RX + 5.4, 6.73, 4.85, 0.72, fc=TEAL, ec=WHITE, lw=0.8, radius=0.12, zorder=4)
txt(RX + 7.825, 7.09, "16 categoricas  |  OHE  -->  309 encoded", fs=8)

arrow_v(RC, 6.65, 5.78, color=TEAL)
tag(RC + 1.2, 6.21, "predict_proba()  -->  float [0, 1]")

# 5 — Classificacao
rbox(RX, 4.48, RW, 1.2, fc=GREEN, ec=EMERALD, lw=1.5, radius=0.2)
txt(RC, 5.32, "Classificacao de Risco de Credito", fs=11)

levels = [
    (RX + 0.28, "BAIXO RISCO", "Prob. < 30%",  EMERALD),
    (RX + 3.83, "MEDIO RISCO", "Prob. 30-70%", AMBER),
    (RX + 7.38, "ALTO RISCO",  "Prob. >= 70%", RED),
]
for lx, name, pct, fc in levels:
    rbox(lx, 4.57, 3.1, 0.75, fc=fc, ec=WHITE, lw=0.8, radius=0.12, zorder=4)
    txt(lx + 1.55, 4.99, name, fs=8.2)
    txt(lx + 1.55, 4.71, pct,  fs=7.5, weight="normal")

arrow_v(RC, 4.48, 3.6, color=GREEN)

# 6 — Log
rbox(RX, 2.25, RW, 1.25, fc=DARK, radius=0.2)
txt(RC, 3.15, "Resultado  &  Logging  |  utils/db.py", fs=10.5)
txt(RC, 2.82, "prediction: 0|1   |   probability: float   |   Exibicao no Streamlit", fs=8.5, weight="normal")
txt(RC, 2.54, "PostgreSQL  |  timestamp  |  inputs  |  output  |  model_version=v3", fs=8.2, weight="normal")
txt(RC, 2.32, "Registro auditavel de todas as predicoes em producao", fs=7.5, weight="normal", alpha=0.75)

# ══════════════════════════════════════════════════════════════════════════════
#  BARRA DE INFRAESTRUTURA
# ══════════════════════════════════════════════════════════════════════════════
rbox(0.3, 0.08, W - 0.6, 2.07, fc="#1C2836", ec=DARK, lw=1.2, radius=0.25, zorder=2)
txt(W / 2, 1.98, "INFRAESTRUTURA  |  Docker Compose", fs=9, color="#94A3B8")

infra = [
    (0.5,   "Docker Compose",  "Orquestra toda a stack\n8501 | 8082 | 9100 | 5433"),
    (5.3,   "Apache Airflow",  "Orquestracao do pipeline\nWebserver :8082"),
    (10.1,  "PostgreSQL 16",   "Logging de predicoes\ncreditguard :5433"),
    (14.9,  "MinIO",           "Object storage (S3-compatible)\nAPI :9100 | Console :9101"),
    (19.7,  "Python 3.12",     "scikit-learn==1.7.0 (pinado)\nlightgbm | xgboost | streamlit"),
]
for ix, title, sub in infra:
    rbox(ix, 0.16, 4.5, 1.65, fc=GRAY, ec="#4B5563", lw=0.8, radius=0.15, zorder=3)
    txt(ix + 2.25, 1.28, title, fs=8.5, color=WHITE)
    txt(ix + 2.25, 0.82, sub, fs=7.3, color="#D1D5DB", weight="normal", alpha=0.9)

# ══════════════════════════════════════════════════════════════════════════════
#  LEGENDA
# ══════════════════════════════════════════════════════════════════════════════
legend_items = [
    mpatches.Patch(color=NAVY,  label="Ingestao / Dados brutos"),
    mpatches.Patch(color=BLUE,  label="Processamento / Transformacao"),
    mpatches.Patch(color=SKY,   label="Camada de features"),
    mpatches.Patch(color=GREEN, label="Modelo vencedor / Output"),
    mpatches.Patch(color=TEAL,  label="Storage / Artefatos"),
    mpatches.Patch(color=GRAY,  label="Infraestrutura"),
]
leg = ax.legend(handles=legend_items, loc="lower right",
                bbox_to_anchor=(0.998, 0.132),
                fontsize=7.8, framealpha=0.95,
                edgecolor=DIVIDER, facecolor=WHITE,
                title="Legenda", title_fontsize=8.5)

# ── Rodape ────────────────────────────────────────────────────────────────────
ax.text(0.005, 0.012,
        "CreditGuard AI  |  ProScore Analytics  |  Metodologia CRISP-DM  |  MBA - Engenharia de Machine Learning",
        fontsize=6.8, color=LGRAY, ha="left", va="bottom",
        transform=ax.transAxes)

# ── Salvar ────────────────────────────────────────────────────────────────────
out = "docs/architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print(f"Diagrama salvo: {out}")
plt.close()
