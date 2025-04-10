from uprchat.app.db_config import get_session
from sqlmodel import Session, select, delete
from uprchat.app.models import CrawlerData


class HarvesterRepository:
    def __init__(self):
        self.session: Session = get_session()

    def saveData(self, data: CrawlerData):
        self.session.add(data)
        self.session.commit()

    def getData(self, data_uri: str):
        return self.session.exec(
            select(CrawlerData).where(CrawlerData.uri == data_uri)
        ).first()
        
    def get_all_data(self):
        return self.session.exec(select(CrawlerData))
