import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

from LanguagePopularitySource import LanguagePopularitySource


class GithubVisualizer:
    MISSING_LANGUAGE_LABEL = "Sem linguagem definida"
    NO_ISSUES_LABEL = "Sem issues (razão indefinida)"
    HIGH_RATIO_THRESHOLD = 0.75
    ISSUE_RATIO_BINS = [0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0]
    ISSUE_RATIO_LABELS = ["0–10%", "10–25%", "25–50%", "50–75%", "75–90%", "90–100%"]

    COLOR_POPULAR = "#2a78d6"
    COLOR_OTHER = "#eb6834"
    COLOR_INK = "#0b0b0b"
    COLOR_INK_SECONDARY = "#52514e"
    COLOR_MUTED = "#898781"
    COLOR_GRID = "#e1e0d9"

    def __init__(self, csv_path="repositorios_1000.csv", output_dir="graficos"):
        self.csv_path = csv_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.df = pd.read_csv(csv_path)
        numeric_cols = [
            "total_pull_requests",
            "total_pull_requests_aceitas",
            "total_releases",
            "dias_desde_ultima_atualizacao",
            "razao_issues_fechadas",
            "idade_em_anos",
            "idade_em_dias",
        ]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        sns.set_theme(style="whitegrid")

    def _save(self, fig, filename):
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"Gráfico salvo em: {path}")
        return path

    def plot_releases_distribution(self):
        data = self.df["total_releases"].dropna()

        bins = [-1, 0, 10, 50, 100, 500, float("inf")]
        labels = [
            "0",
            "1–10",
            "11–50",
            "51–100",
            "101–500",
            ">500"
        ]

        faixas = pd.cut(
            data,
            bins=bins,
            labels=labels
        )

        distribuicao = faixas.value_counts().reindex(labels, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 5))

        distribuicao.plot(
            kind="barh",
            ax=ax
        )

        ax.set_title(
            "Distribuição dos Repositórios por Número de Releases"
        )
        ax.set_xlabel("Número de Repositórios")
        ax.set_ylabel("Total de Releases")

        for i, valor in enumerate(distribuicao):
            ax.text(
                valor + max(distribuicao) * 0.01,
                i,
                str(valor),
                va="center",
                fontsize=10
            )

        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)

        fig.tight_layout()

        return self._save(
            fig,
            "distribuicao_total_releases.png"
        )

    def median_pull_requests_aceitas(self):
        data = self.df["total_pull_requests_aceitas"].dropna()
        mediana = data.median()
        print(f"Mediana de pull requests aceitas: {mediana}")
        return mediana

    def plot_pull_requests_aceitas_distribution(self):
        data = self.df["total_pull_requests_aceitas"].dropna()
        mediana = data.median()

        bins = [-1, 0, 10, 50, 100, 500, float("inf")]
        labels = [
            "0",
            "1–10",
            "11–50",
            "51–100",
            "101–500",
            ">500"
        ]

        faixas = pd.cut(
            data,
            bins=bins,
            labels=labels
        )

        distribuicao = faixas.value_counts().reindex(labels, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 5))

        distribuicao.plot(
            kind="barh",
            ax=ax
        )

        ax.set_title(
            f"Distribuição dos Repositórios por Total de PRs Aceitas (Mediana = {mediana:.0f})"
        )
        ax.set_xlabel("Número de Repositórios")
        ax.set_ylabel("Total de Pull Requests Aceitas")

        for i, valor in enumerate(distribuicao):
            ax.text(
                valor + max(distribuicao) * 0.01,
                i,
                str(valor),
                va="center",
                fontsize=10
            )

        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)

        fig.tight_layout()

        return self._save(
            fig,
            "distribuicao_total_pull_requests_aceitas.png"
        )

    def _titles(self, ax, title, subtitle=None):
        ax.set_title(
            title,
            loc="left",
            fontsize=13,
            color=self.COLOR_INK,
            pad=30 if subtitle else 14
        )
        if subtitle:
            ax.text(
                0,
                1.015,
                subtitle,
                transform=ax.transAxes,
                fontsize=9.5,
                color=self.COLOR_INK_SECONDARY
            )

    def _footnote(self, fig, text):
        fig.text(
            0.01,
            0.008,
            text,
            fontsize=7.5,
            color=self.COLOR_MUTED,
            va="bottom"
        )

    def _source_footer(self, fig):
        self._footnote(fig, LanguagePopularitySource.citation())

    def count_by_primary_language(self, include_missing=True):
        languages = self.df["linguagem_primaria"].fillna(self.MISSING_LANGUAGE_LABEL)
        counts = languages.value_counts()
        if not include_missing:
            counts = counts.drop(self.MISSING_LANGUAGE_LABEL, errors="ignore")
        return counts

    def build_language_count_table(self):
        counts = self.count_by_primary_language()
        total = int(counts.sum())
        ranking = self.count_by_primary_language(include_missing=False)
        positions = {language: position for position, language in enumerate(ranking.index, start=1)}

        table = pd.DataFrame({
            "linguagem": list(counts.index),
            "repositorios": counts.to_numpy()
        })
        table["percentual"] = (table["repositorios"] / total * 100).round(2)
        table["posicao_dataset"] = table["linguagem"].map(positions)
        table["posicao_fonte"] = table["linguagem"].map(LanguagePopularitySource.rank_of)
        table["no_top10_fonte"] = table["posicao_fonte"].notna()
        return table

    def popular_language_coverage(self):
        counts = self.count_by_primary_language(include_missing=False)
        total = len(self.df)
        with_language = int(counts.sum())
        in_source = int(sum(
            valor for linguagem, valor in counts.items()
            if LanguagePopularitySource.is_popular(linguagem)
        ))
        return {
            "total_repositorios": total,
            "com_linguagem": with_language,
            "sem_linguagem": total - with_language,
            "no_top10_fonte": in_source,
            "percentual_do_total": round(in_source / total * 100, 1),
            "percentual_dos_com_linguagem": round(in_source / with_language * 100, 1)
        }

    def plot_primary_language_count(self, top_n=15):
        counts = self.count_by_primary_language(include_missing=False).head(top_n)
        coverage = self.popular_language_coverage()
        maximo = int(counts.max())

        colors = [
            self.COLOR_POPULAR if LanguagePopularitySource.is_popular(linguagem) else self.COLOR_OTHER
            for linguagem in counts.index
        ]

        fig, ax = plt.subplots(figsize=(10, 7))
        posicoes = list(range(len(counts)))

        ax.barh(posicoes, counts.to_numpy(), color=colors, height=0.62)
        ax.set_yticks(posicoes)
        ax.set_yticklabels(list(counts.index))
        ax.invert_yaxis()

        for posicao, valor in zip(posicoes, counts.to_numpy()):
            ax.text(
                valor + maximo * 0.012,
                posicao,
                f"{valor} ({valor / coverage['total_repositorios']:.1%})",
                va="center",
                fontsize=9,
                color=self.COLOR_INK_SECONDARY
            )

        self._titles(
            ax,
            f"Linguagem primária dos {coverage['total_repositorios']} repositórios mais estrelados",
            f"Top {len(counts)} linguagens · {coverage['sem_linguagem']} repositórios "
            f"sem linguagem primária não aparecem no gráfico"
        )
        ax.set_xlabel("Número de repositórios", fontsize=10, color=self.COLOR_INK_SECONDARY)
        ax.set_ylabel("")
        ax.set_xlim(0, maximo * 1.2)

        handles = [
            plt.Rectangle((0, 0), 1, 1, color=self.COLOR_POPULAR),
            plt.Rectangle((0, 0), 1, 1, color=self.COLOR_OTHER)
        ]
        ax.legend(
            handles,
            [
                f"No top 10 do {LanguagePopularitySource.SHORT_NAME}",
                f"Fora do top 10 do {LanguagePopularitySource.SHORT_NAME}"
            ],
            loc="lower right",
            frameon=False,
            fontsize=9,
            labelcolor=self.COLOR_INK_SECONDARY
        )

        ax.grid(axis="x", color=self.COLOR_GRID, linewidth=1, alpha=0.9)
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)

        self._source_footer(fig)
        fig.tight_layout(rect=(0, 0.07, 1, 1))

        return self._save(fig, "contagem_linguagem_primaria.png")

    def plot_language_popularity_comparison(self):
        counts = self.count_by_primary_language(include_missing=False)
        positions = {linguagem: posicao for posicao, linguagem in enumerate(counts.index, start=1)}
        coverage = self.popular_language_coverage()

        referencia = LanguagePopularitySource.TOP_LANGUAGES
        limite = max([positions[l] for l in referencia if l in positions] + [len(referencia)])

        fig, ax = plt.subplots(figsize=(10, 6.5))
        faixa = 0.15

        for linha, linguagem in enumerate(referencia):
            posicao_fonte = linha + 1
            posicao_dataset = positions.get(linguagem)

            if posicao_dataset is not None:
                ax.plot(
                    [posicao_fonte, posicao_dataset],
                    [linha - faixa, linha + faixa],
                    color=self.COLOR_GRID,
                    linewidth=2,
                    zorder=1
                )
                ax.scatter(
                    posicao_dataset,
                    linha + faixa,
                    s=90,
                    color=self.COLOR_OTHER,
                    zorder=3,
                    edgecolors="white",
                    linewidths=2
                )
                ax.text(
                    posicao_dataset,
                    linha - 0.42,
                    f"{posicao_dataset}º",
                    ha="center",
                    fontsize=8.5,
                    color=self.COLOR_INK_SECONDARY
                )
            else:
                ax.text(
                    posicao_fonte + 0.7,
                    linha,
                    f"nenhum repositório entre os {coverage['total_repositorios']} mais estrelados",
                    va="center",
                    fontsize=8.5,
                    color=self.COLOR_MUTED
                )

            ax.scatter(
                posicao_fonte,
                linha - faixa,
                s=90,
                color=self.COLOR_POPULAR,
                zorder=3,
                edgecolors="white",
                linewidths=2
            )

        ax.set_yticks(list(range(len(referencia))))
        ax.set_yticklabels([
            f"{posicao}. {linguagem}" for posicao, linguagem in enumerate(referencia, start=1)
        ])
        ax.invert_yaxis()
        ax.set_ylim(len(referencia) - 0.4, -0.8)

        self._titles(
            ax,
            f"Linguagens mais populares ({LanguagePopularitySource.SHORT_NAME}) x repositórios mais estrelados",
            f"{coverage['no_top10_fonte']} dos {coverage['total_repositorios']} repositórios "
            f"({coverage['percentual_do_total']}%) usam uma das 10 linguagens da fonte"
        )
        ax.set_xlabel(
            "Posição no ranking (1 = mais popular)",
            fontsize=10,
            color=self.COLOR_INK_SECONDARY
        )
        ax.set_xlim(0, limite + 5)
        ax.set_xticks([1] + list(range(5, limite + 1, 5)))

        handles = [
            plt.Line2D([], [], marker="o", linestyle="", markersize=9, color=self.COLOR_POPULAR),
            plt.Line2D([], [], marker="o", linestyle="", markersize=9, color=self.COLOR_OTHER)
        ]
        ax.legend(
            handles,
            [
                f"Posição no {LanguagePopularitySource.SHORT_NAME}",
                "Posição entre os repositórios mais estrelados"
            ],
            loc="upper right",
            frameon=False,
            fontsize=9,
            labelcolor=self.COLOR_INK_SECONDARY
        )

        ax.grid(axis="x", color=self.COLOR_GRID, linewidth=1, alpha=0.9)
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)

        self._source_footer(fig)
        fig.tight_layout(rect=(0, 0.075, 1, 1))

        return self._save(fig, "comparacao_linguagens_populares.png")

    def plot_days_since_update(self):
        data = self.df["dias_desde_ultima_atualizacao"].dropna()
        data = data[data >= 0]

        q1 = data.quantile(0.25)
        mediana = data.median()
        q3 = data.quantile(0.75)
        media = data.mean()
        p90 = data.quantile(0.90)

        ate_30 = (data <= 30).mean() * 100
        ate_90 = (data <= 90).mean() * 100
        ate_365 = (data <= 365).mean() * 100
        mais_1_ano = (data > 365).mean() * 100

        fig, ax = plt.subplots(figsize=(13, 5))

        sns.boxplot(
            x=data,
            ax=ax,
            width=0.4,
            showfliers=True,
            flierprops=dict(
                marker="o",
                markersize=3,
                alpha=0.2
            )
        )

        ax.set_xscale("symlog", linthresh=1)

        ax.axvline(
            mediana,
            linestyle="--",
            linewidth=2,
            label=f"Mediana: {mediana:.0f} dias"
        )

        ax.set_title(
            "Dias Desde a Última Atualização dos 1.000 Repositórios",
            fontsize=15,
            fontweight="bold",
            pad=15
        )

        ax.set_xlabel(
            "Dias desde a última atualização",
            fontsize=11
        )

        ax.set_yticks([])

        texto = (
            f"Q1: {q1:,.0f} dias\n"
            f"Mediana: {mediana:,.0f} dias\n"
            f"Q3: {q3:,.0f} dias\n"
            f"Média: {media:,.0f} dias\n"
            f"P90: {p90:,.0f} dias"
        )

        ax.text(
            0.98,
            0.90,
            texto,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="white",
                edgecolor="gray",
                alpha=0.95
            )
        )

        resumo = (
            f"≤ 30 dias: {ate_30:.1f}%   |   "
            f"≤ 90 dias: {ate_90:.1f}%   |   "
            f"≤ 1 ano: {ate_365:.1f}%   |   "
            f"> 1 ano: {mais_1_ano:.1f}%"
        )

        fig.text(
            0.5,
            0.02,
            resumo,
            ha="center",
            fontsize=10
        )

        ax.grid(
            axis="x",
            linestyle="--",
            alpha=0.2
        )

        ax.legend(
            loc="upper left",
            fontsize=9,
            frameon=True
        )

        plt.tight_layout(rect=[0, 0.08, 1, 1])

        return self._save(
            fig,
            "dias_desde_atualizacao.png"
        )

    def median_repository_age(self):
        data = self.df["idade_em_anos"].dropna()
        mediana = data.median()
        print(f"Mediana da idade dos repositórios: {mediana:.1f} anos")
        return mediana

    def plot_repository_age_distribution(self):
        data = self.df["idade_em_anos"].dropna()

        q1 = data.quantile(0.25)
        mediana = data.median()
        q3 = data.quantile(0.75)
        media = data.mean()
        p90 = data.quantile(0.90)

        ate_2 = (data <= 2).mean() * 100
        ate_5 = (data <= 5).mean() * 100
        ate_10 = (data <= 10).mean() * 100
        mais_10 = (data > 10).mean() * 100

        fig, ax = plt.subplots(figsize=(13, 5))

        sns.boxplot(
            x=data,
            ax=ax,
            width=0.4,
            showfliers=True,
            flierprops=dict(
                marker="o",
                markersize=3,
                alpha=0.2
            )
        )

        ax.axvline(
            mediana,
            linestyle="--",
            linewidth=2,
            label=f"Mediana: {mediana:.1f} anos"
        )

        ax.set_title(
            "Idade dos 1.000 Repositórios Mais Estrelados",
            fontsize=15,
            fontweight="bold",
            pad=15
        )

        ax.set_xlabel(
            "Idade do repositório (anos)",
            fontsize=11
        )

        ax.set_yticks([])

        texto = (
            f"Q1: {q1:,.1f} anos\n"
            f"Mediana: {mediana:,.1f} anos\n"
            f"Q3: {q3:,.1f} anos\n"
            f"Média: {media:,.1f} anos\n"
            f"P90: {p90:,.1f} anos"
        )

        ax.text(
            0.98,
            0.90,
            texto,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="white",
                edgecolor="gray",
                alpha=0.95
            )
        )

        resumo = (
            f"≤ 2 anos: {ate_2:.1f}%   |   "
            f"≤ 5 anos: {ate_5:.1f}%   |   "
            f"≤ 10 anos: {ate_10:.1f}%   |   "
            f"> 10 anos: {mais_10:.1f}%"
        )

        fig.text(
            0.5,
            0.02,
            resumo,
            ha="center",
            fontsize=10
        )

        ax.grid(
            axis="x",
            linestyle="--",
            alpha=0.2
        )

        ax.legend(
            loc="upper left",
            fontsize=9,
            frameon=True
        )

        plt.tight_layout(rect=[0, 0.08, 1, 1])

        return self._save(
            fig,
            "distribuicao_idade_repositorios.png"
        )

    def plot_language_comparison_heatmap(self, top_n=10):
        grouped = self.df.groupby("linguagem_primaria").agg(
            repositorios=("linguagem_primaria", "count"),
            media_prs_aceitas=("total_pull_requests_aceitas", "mean"),
            media_releases=("total_releases", "mean"),
            media_dias_atualizacao=("dias_desde_ultima_atualizacao", "mean"),
        )

        grouped = grouped.sort_values("repositorios", ascending=False).head(top_n)

        max_dias = grouped["media_dias_atualizacao"].max()
        grouped["frequencia_atualizacao"] = max_dias - grouped["media_dias_atualizacao"]

        display_cols = {
            "media_prs_aceitas": "Média PRs Aceitas\n(RQ02)",
            "media_releases": "Média Releases\n(RQ03)",
            "frequencia_atualizacao": "Frequência de Atualização\n(RQ04)",
        }
        heat_data = grouped[list(display_cols.keys())].rename(columns=display_cols)

        normalized = (heat_data - heat_data.min()) / (heat_data.max() - heat_data.min())

        annot = heat_data.copy()
        annot["Média PRs Aceitas\n(RQ02)"] = annot["Média PRs Aceitas\n(RQ02)"].round(1)
        annot["Média Releases\n(RQ03)"] = annot["Média Releases\n(RQ03)"].round(1)
        annot["Frequência de Atualização\n(RQ04)"] = grouped["media_dias_atualizacao"].round(0).astype(
            int).astype(str) + " dias"

        fig, ax = plt.subplots(figsize=(9, 0.6 * len(heat_data) + 2))
        sns.heatmap(
            normalized,
            annot=annot,
            fmt="",
            cmap="YlGnBu",
            linewidths=0.5,
            linecolor="white",
            cbar_kws={"label": "Posição relativa entre as linguagens (normalizado)"},
            ax=ax
        )

        ax.set_title(
            f"Comparação por Linguagem: Contribuição, Releases e Atualização (Top {top_n})",
            fontsize=13, fontweight="bold", pad=15
        )
        ax.set_xlabel("")
        ax.set_ylabel("Linguagem Primária")
        ax.tick_params(axis="y", rotation=0)

        fig.tight_layout()
        return self._save(fig, "comparacao_linguagens_rq07.png")

    def plot_language_diversity_vs_contribution(self):
        df = self.df.copy()

        def contar_linguagens(valor):
            if not isinstance(valor, str) or not valor.strip():
                return None
            itens = [v.strip() for v in valor.split(",") if v.strip() and v.strip() != "Sem informação"]
            return len(itens) if itens else None

        df["diversidade_linguagens"] = df["linguagens"].apply(contar_linguagens)

        data = df.dropna(subset=["diversidade_linguagens", "total_pull_requests_aceitas"])
        data = data[data["total_pull_requests_aceitas"] >= 0]

        r, p = pearsonr(data["diversidade_linguagens"], data["total_pull_requests_aceitas"])

        rng = np.random.default_rng(42)
        jitter = rng.uniform(-0.18, 0.18, size=len(data))
        x_jitter = data["diversidade_linguagens"].to_numpy() + jitter

        fig, ax = plt.subplots(figsize=(10, 7))

        scatter = ax.scatter(
            x_jitter,
            data["total_pull_requests_aceitas"],
            c=data["razao_issues_fechadas"],
            cmap="RdYlGn",
            alpha=0.45,
            s=35,
            edgecolor="white",
            linewidth=0.3,
            zorder=1
        )

        sns.regplot(
            x="diversidade_linguagens",
            y="total_pull_requests_aceitas",
            data=data,
            scatter=False,
            ax=ax,
            color="#1f3d7a",
            line_kws={"linestyle": "-", "linewidth": 3.5, "zorder": 5},
            ci=95
        )

        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Razão de Issues Fechadas (RQ06)")

        significancia = "significativa" if p < 0.05 else "não significativa"

        ax.set_title(
            f"Correlação de Pearson: r = {r:.3f}   (p = {p:.4f}, {significancia})",
            fontsize=10, style="italic", pad=8
        )
        fig.suptitle(
            "Diversidade Linguística vs. Contribuição Externa e Qualidade de Manutenção",
            fontsize=13, fontweight="bold", y=0.98
        )

        ax.set_xticks(sorted(data["diversidade_linguagens"].unique()))
        ax.set_xlabel("Nº de Linguagens Distintas no Repositório")
        ax.set_ylabel("Total de Pull Requests Aceitas")

        ax.set_yscale("symlog", linthresh=1000)
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.2, which="both")

        fig.tight_layout(rect=[0, 0, 1, 0.94])
        return self._save(fig, "diversidade_linguagens_vs_contribuicao.png")

    def closed_issues_ratio(self):
        total = self.df["total_issues"]
        closed = self.df["issues_fechadas"]
        # total == 0 vira NaN: 0/0 e indefinido e nao equivale a 0% de fechamento
        return closed / total.where(total > 0)

    def closed_issues_ratio_stats(self):
        ratio = self.closed_issues_ratio()
        com_issues = ratio.dropna()
        total = len(ratio)

        return {
            "total_repositorios": total,
            "com_issues": len(com_issues),
            "sem_issues": total - len(com_issues),
            "mediana": round(float(com_issues.median()), 4),
            "media": round(float(com_issues.mean()), 4),
            "desvio_padrao": round(float(com_issues.std()), 4),
            "minimo": round(float(com_issues.min()), 4),
            "maximo": round(float(com_issues.max()), 4),
            "p10": round(float(com_issues.quantile(0.10)), 4),
            "p25": round(float(com_issues.quantile(0.25)), 4),
            "p75": round(float(com_issues.quantile(0.75)), 4),
            "p90": round(float(com_issues.quantile(0.90)), 4),
            "acima_do_limiar": int((com_issues >= self.HIGH_RATIO_THRESHOLD).sum()),
            "totalmente_fechadas": int((com_issues >= 1).sum())
        }

    def build_closed_issues_ratio_table(self):
        ratio = self.closed_issues_ratio()
        com_issues = ratio.dropna()

        faixas = pd.cut(
            com_issues,
            bins=self.ISSUE_RATIO_BINS,
            labels=self.ISSUE_RATIO_LABELS,
            include_lowest=True
        )
        contagem = faixas.value_counts().reindex(self.ISSUE_RATIO_LABELS, fill_value=0)

        table = pd.DataFrame({
            "faixa": self.ISSUE_RATIO_LABELS + [self.NO_ISSUES_LABEL],
            "repositorios": list(contagem.to_numpy()) + [len(ratio) - len(com_issues)]
        })
        table["percentual_do_total"] = (table["repositorios"] / len(ratio) * 100).round(2)
        table["percentual_dos_com_issues"] = (
            table["repositorios"] / len(com_issues) * 100
        ).round(2)
        table.loc[table["faixa"] == self.NO_ISSUES_LABEL, "percentual_dos_com_issues"] = None
        return table

    def print_closed_issues_ratio_summary(self):
        stats = self.closed_issues_ratio_stats()
        print(
            f"Razão issues fechadas/total — mediana: {stats['mediana']} "
            f"({stats['mediana']:.1%}) em {stats['com_issues']} repositórios com issues; "
            f"{stats['sem_issues']} repositórios com 0 issues (razão indefinida) "
            f"ficam fora do cálculo"
        )
        return stats

    def plot_closed_issues_ratio_distribution(self, bin_width=0.05):
        stats = self.closed_issues_ratio_stats()
        com_issues = self.closed_issues_ratio().dropna()

        arestas = np.arange(0, 1 + bin_width, bin_width)
        contagem, arestas = np.histogram(com_issues, bins=arestas)
        centros = (arestas[:-1] + arestas[1:]) / 2
        maximo = int(contagem.max())

        colors = [
            self.COLOR_POPULAR if inicio >= self.HIGH_RATIO_THRESHOLD else self.COLOR_OTHER
            for inicio in arestas[:-1]
        ]

        fig, ax = plt.subplots(figsize=(11, 6))
        ax.bar(
            centros,
            contagem,
            width=bin_width,
            color=colors,
            edgecolor="white",
            linewidth=0.9,
            zorder=2
        )

        for centro, valor in zip(centros, contagem):
            if valor == 0:
                continue
            ax.text(
                centro,
                valor + maximo * 0.018,
                str(valor),
                ha="center",
                fontsize=8,
                color=self.COLOR_INK_SECONDARY,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8),
                zorder=5
            )

        ax.axvline(
            stats["mediana"],
            color=self.COLOR_INK,
            linewidth=1.6,
            linestyle="--",
            zorder=4
        )
        ax.text(
            stats["mediana"] - 0.012,
            maximo * 0.98,
            f"mediana {stats['mediana']:.1%}",
            ha="right",
            va="top",
            fontsize=9.5,
            color=self.COLOR_INK
        )

        self._titles(
            ax,
            f"Razão de issues fechadas dos {stats['total_repositorios']} "
            f"repositórios mais estrelados",
            f"Mediana de {stats['mediana']:.1%} entre os {stats['com_issues']} repositórios "
            f"com issues · cada barra é uma faixa de {bin_width * 100:.0f} pontos percentuais"
        )
        ax.set_xlabel(
            "Issues fechadas / total de issues (%)",
            fontsize=10,
            color=self.COLOR_INK_SECONDARY
        )
        ax.set_ylabel("Número de repositórios", fontsize=10, color=self.COLOR_INK_SECONDARY)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, maximo * 1.16)
        ax.set_xticks(arestas)
        ax.set_xticklabels([f"{aresta * 100:.0f}" for aresta in arestas], fontsize=8.5)
        ax.tick_params(axis="x", length=3, color=self.COLOR_GRID)

        limiar = self.HIGH_RATIO_THRESHOLD
        acima = stats["acima_do_limiar"]
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=self.COLOR_POPULAR),
            plt.Rectangle((0, 0), 1, 1, color=self.COLOR_OTHER)
        ]
        ax.legend(
            handles,
            [
                f"≥ {limiar:.0%} fechadas — {acima} repositórios "
                f"({acima / stats['com_issues']:.1%} dos que têm issues)",
                f"< {limiar:.0%} fechadas — {stats['com_issues'] - acima} repositórios"
            ],
            loc="upper left",
            frameon=False,
            fontsize=9,
            labelcolor=self.COLOR_INK_SECONDARY
        )

        ax.grid(axis="y", color=self.COLOR_GRID, linewidth=1, alpha=0.9)
        ax.grid(axis="x", visible=False)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)

        self._footnote(
            fig,
            "Razão = issues fechadas / total de issues (campos totalIssues e closedIssues da API "
            "GraphQL do GitHub).\n"
            f"{stats['sem_issues']} dos {stats['total_repositorios']} repositórios têm 0 issues: "
            "a razão seria 0/0, indefinida, e por isso não entram na mediana nem no gráfico "
            "(ex.: torvalds/linux, git/git, django/django, que não usam o issue tracker do GitHub)."
        )
        fig.tight_layout(rect=(0, 0.075, 1, 1))

        return self._save(fig, "distribuicao_razao_issues_fechadas.png")

    def generate_all(self):
        self.plot_releases_distribution()
        self.median_pull_requests_aceitas()
        self.plot_pull_requests_aceitas_distribution()
        self.median_repository_age()
        self.plot_repository_age_distribution()
        self.plot_primary_language_count()
        self.plot_language_popularity_comparison()
        self.print_closed_issues_ratio_summary()
        self.plot_closed_issues_ratio_distribution()


if __name__ == "__main__":
    viz = GithubVisualizer("repositorios_1000.csv")
    viz.generate_all()