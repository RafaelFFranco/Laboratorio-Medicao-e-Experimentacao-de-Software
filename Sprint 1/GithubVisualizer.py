import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class GithubVisualizer:
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

    def generate_all(self):
        # self.plot_releases_distribution()
        self.plot_days_since_update()


if __name__ == "__main__":
    viz = GithubVisualizer("repositorios_1000.csv")
    viz.generate_all()