class LanguagePopularitySource:
    NAME = "GitHub Octoverse 2025"
    SHORT_NAME = "Octoverse 2025"
    METRIC = "número de desenvolvedores distintos por mês que enviaram código na linguagem"
    PERIOD = "01/09/2024 a 31/08/2025"
    PUBLISHED_AT = "28/10/2025"
    ACCESSED_AT = "25/08/2026"
    URL = "https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/"

    TOP_LANGUAGES = [
        "TypeScript",
        "Python",
        "JavaScript",
        "Java",
        "C#",
        "PHP",
        "Shell",
        "C++",
        "HCL",
        "Go",
    ]

    @classmethod
    def ranking(cls):
        return {language: position for position, language in enumerate(cls.TOP_LANGUAGES, start=1)}

    @classmethod
    def rank_of(cls, language):
        return cls.ranking().get(language)

    @classmethod
    def is_popular(cls, language):
        return language in cls.ranking()

    @classmethod
    def citation(cls):
        return (
            f"Fonte de \"linguagens mais populares\": {cls.NAME} "
            f"(métrica: {cls.METRIC}; período {cls.PERIOD}; "
            f"publicado em {cls.PUBLISHED_AT}, acesso em {cls.ACCESSED_AT}).\n{cls.URL}"
        )


if __name__ == "__main__":
    print(LanguagePopularitySource.citation())
    print()
    for language, position in LanguagePopularitySource.ranking().items():
        print(f"{position:2d}. {language}")
