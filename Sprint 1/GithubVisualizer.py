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
        numeric_cols = ["total_pull_requests_aceitas"]
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

    def generate_all(self):
        self.median_pull_requests_aceitas()
        self.plot_pull_requests_aceitas_distribution()


if __name__ == "__main__":
    viz = GithubVisualizer("repositorios_1000.csv")
    viz.generate_all()
