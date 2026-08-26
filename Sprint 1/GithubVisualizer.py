import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from LanguagePopularitySource import LanguagePopularitySource


class GithubVisualizer:
    MISSING_LANGUAGE_LABEL = "Sem linguagem definida"

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
        numeric_cols = ["total_releases"]
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

    def _source_footer(self, fig):
        fig.text(
            0.01,
            0.008,
            LanguagePopularitySource.citation(),
            fontsize=7.5,
            color=self.COLOR_MUTED,
            va="bottom"
        )

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

    def export_language_counts(self, filename="contagem_linguagem_primaria.csv"):
        path = os.path.join(self.output_dir, filename)
        self.build_language_count_table().to_csv(path, index=False, encoding="utf-8")
        print(f"Contagem por linguagem salva em: {path}")
        return path

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

    def generate_all(self):
        self.plot_releases_distribution()
        self.export_language_counts()
        self.plot_primary_language_count()
        self.plot_language_popularity_comparison()


if __name__ == "__main__":
    viz = GithubVisualizer("repositorios_1000.csv")
    viz.generate_all()