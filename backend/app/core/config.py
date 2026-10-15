from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "Career Intelligence Platform"
    api_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000"
    public_access_enabled: bool = False

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    demo_user_id: str = "00000000-0000-0000-0000-000000000000"
    career_user_id: str = "00000000-0000-0000-0000-000000000000"

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    github_username: str = "Vivekarya05"
    github_token: str = ""

    resend_api_key: str = ""
    email_from: str = Field(default="Career Intelligence <digest@example.com>")
    email_to: str = Field(default="vivek@example.com")
    resume_storage_bucket: str = "resumes"

    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    discovery_location: str = "Australia"
    discovery_countries: str = "Australia"
    discovery_results_per_source: int = 25
    company_career_sources: str = (
        "AEMO|https://aemo.com.au/about/careers|Australia,"
        "Transgrid|https://www.transgrid.com.au/careers|Australia,"
        "Endeavour Energy|https://www.endeavourenergy.com.au/about/careers|Australia,"
        "Ausgrid|https://www.ausgrid.com.au/About-Us/Careers|Australia,"
        "Essential Energy|https://www.essentialenergy.com.au/careers|Australia,"
        "JD Ross Energy|https://www.jdrossenergy.com/|Australia,"
        "Phillip Riley|https://www.phillipriley.com.au/|Australia,"
        "EnergyAustralia|https://www.energyaustralia.com.au/about-us/careers|Australia,"
        "AGL|https://www.agl.com.au/about-agl/careers|Australia,"
        "Origin Energy|https://www.originenergy.com.au/about/careers/|Australia,"
        "AusNet|https://www.ausnetservices.com.au/about/careers|Australia,"
        "Snowy Hydro|https://www.snowyhydro.com.au/careers/|Australia,"
        "Hydro Tasmania|https://www.hydro.com.au/about-us/careers|Australia,"
        "CS Energy|https://www.csenergy.com.au/careers|Australia,"
        "Stanwell|https://www.stanwell.com/careers/|Australia,"
        "Iberdrola Australia|https://www.iberdrola.com.au/careers/|Australia,"
        "Neoen|https://neoen.com/en/careers/|Australia,"
        "Akaysha Energy|https://akayshaenergy.com/careers/|Australia,"
        "Squadron Energy|https://www.squadronenergy.com/careers|Australia,"
        "Tilt Renewables|https://www.tiltrenewables.com/careers/|Australia,"
        "TagEnergy|https://tag-en.com/careers/|Australia,"
        "Fluence|https://fluenceenergy.com/careers/|Australia,"
        "Tesla Energy|https://www.tesla.com/en_au/careers|Australia,"
        "Wartsila|https://www.wartsila.com/careers|Australia,"
        "Aurora Energy Research|https://auroraer.com/careers/|Australia,"
        "EY|https://www.ey.com/en_au/careers|Australia,"
        "Jacobs|https://careers.jacobs.com/|Australia,"
        "GHD|https://www.ghd.com/en/careers|Australia,"
        "Aurecon|https://www.aurecongroup.com/careers|Australia,"
        "AFRY|https://afry.com/en/career|Australia,"
        "Deloitte|https://www.deloitte.com/au/en/careers.html|Australia,"
        "KPMG|https://kpmg.com/au/en/home/careers.html|Australia,"
        "PwC|https://www.pwc.com.au/careers.html|Australia,"
        "Rystad Energy|https://www.rystadenergy.com/careers|Australia,"
        "RepuTex|https://www.reputex.com/careers/|Australia,"
        "ACIL Allen|https://acilallen.com.au/careers/|Australia,"
        "Baringa|https://www.baringa.com/en/careers/|Australia,"
        "GridBeyond|https://gridbeyond.com/careers/|Australia,"
        "Enel X|https://corporate.enelx.com/en/careers|Australia,"
        "Shell Energy|https://shellenergy.com.au/about-us/careers/|Australia,"
        "ENGIE|https://www.engie.com.au/careers|Australia,"
        "Ampol Energy|https://www.ampol.com.au/about-ampol/careers|Australia,"
        "Alinta Energy|https://www.alintaenergy.com.au/about-us/careers|Australia,"
        "Ampyr Energy|https://www.ampyrenergy.com/careers|Australia,"
        "CEP Energy|https://www.cep.energy/careers|Australia,"
        "Edify Energy|https://edifyenergy.com/careers/|Australia,"
        "Pacific Blue|https://pacificblue.com.au/careers/|Australia,"
        "ACCIONA Energia|https://www.acciona.com/careers/|Australia,"
        "Australian Energy Council|https://www.energycouncil.com.au/about/careers/|Australia,"
        "ARENA|https://arena.gov.au/about/careers/|Australia,"
        "CEFC|https://www.cefc.com.au/careers/|Australia,"
        "NSW EnergyCo|https://www.energyco.nsw.gov.au/careers|Australia,"
        "DCCEEW|https://www.dcceew.gov.au/about/careers|Australia"
    )

    @property
    def discovery_country_list(self) -> list[str]:
        return [country.strip() for country in self.discovery_countries.split(",") if country.strip()]

    @property
    def company_career_source_list(self) -> list[tuple[str, str, str]]:
        sources: list[tuple[str, str, str]] = []
        for item in self.company_career_sources.split(","):
            if "|" not in item:
                continue
            parts = [part.strip() for part in item.split("|")]
            if len(parts) == 2:
                company, url = parts
                country = "Australia"
            else:
                company, url, country = parts[:3]
            company = company.strip()
            url = url.strip()
            if company and url:
                sources.append((company, url, country or "Australia"))
        return sources

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        if self.frontend_base_url and self.frontend_base_url not in origins:
            origins.append(self.frontend_base_url)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
