from fastapi import APIRouter
from typing import List
from schemas import SectorItem

router = APIRouter(prefix="/sectors", tags=["Sektörler"])

SECTOR_LIST: List[SectorItem] = [
    SectorItem(nace_code="01.01.01", name="Tarım ve Hayvancılık"),
    SectorItem(nace_code="01.02.01", name="Gıda Üretimi"),
    SectorItem(nace_code="02.01.01", name="Tekstil ve Moda"),
    SectorItem(nace_code="03.01.01", name="Yazılım ve Bilişim"),
    SectorItem(nace_code="04.01.01", name="Eğitim ve Danışmanlık"),
    SectorItem(nace_code="05.01.01", name="Sağlık ve Medikal"),
    SectorItem(nace_code="06.01.01", name="Enerji ve Çevre"),
    SectorItem(nace_code="07.01.01", name="İnşaat ve Mimarlık"),
    SectorItem(nace_code="08.01.01", name="Finans ve Sigorta"),
    SectorItem(nace_code="09.01.01", name="Lojistik ve Taşımacılık"),
    SectorItem(nace_code="10.01.01", name="Savunma Sanayi"),
    SectorItem(nace_code="11.01.01", name="Otomotiv ve Ulaşım"),
    SectorItem(nace_code="12.01.01", name="Turizm ve Otelcilik"),
    SectorItem(nace_code="13.01.01", name="Medya ve Yayıncılık"),
    SectorItem(nace_code="14.01.01", name="Hukuk ve Mevzuat"),
    SectorItem(nace_code="15.01.01", name="Spor ve Rekreasyon"),
    SectorItem(nace_code="16.01.01", name="Sanat ve Kültür"),
    SectorItem(nace_code="17.01.01", name="Kimya ve İlaç"),
    SectorItem(nace_code="18.01.01", name="Elektronik ve Donanım"),
    SectorItem(nace_code="19.01.01", name="Blockchain ve Yapay Zeka")
]

@router.get("/", response_model=List[SectorItem])
def get_sectors() -> List[SectorItem]:
    return SECTOR_LIST