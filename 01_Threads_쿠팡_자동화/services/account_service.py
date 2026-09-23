from typing import List, Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Account
from domain_types.schemas import AccountDTO

class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)

    def list_accounts(self, project_id: Optional[int] = None) -> List[Account]:
        return self.repo.list_accounts(project_id=project_id)

    def get_account(self, account_id: int) -> Optional[Account]:
        return self.repo.get_account(account_id)

    def create_account(self, data: dict) -> Account:
        return self.repo.create_account(data)

    def delete_account(self, account_id: int) -> bool:
        return self.repo.delete_account(account_id)

    def update_account_warmup(self, account_id: int, warmup_status: str) -> Optional[Account]:
        return self.repo.update_account_warmup(account_id, warmup_status)

    def update_account_token(self, account_id: int, access_token: str) -> Optional[Account]:
        acc = self.get_account(account_id)
        if acc:
            acc.access_token = access_token.strip()
            self.db.commit()
            self.db.refresh(acc)
        return acc

    def find_best_account_for_product(self, product_category: str, product_name: str = "") -> Optional[Account]:
        """
        Smart Account Router for Multi-Account Setup:
        1. Look for Vertical Account matching product category
        2. If not found, look for Persona Account matching tone/theme
        3. Fallback to first active account
        """
        accounts = self.list_accounts()
        if not accounts:
            return None

        import re
        # 1. Check exact or partial category match in Vertical accounts
        for acc in accounts:
            if acc.cluster_type == "VERTICAL" and acc.category:
                tokens = [t.strip() for t in re.split(r'[,/ ]+', acc.category) if len(t.strip()) >= 2]
                if any(t in product_category for t in tokens):
                    return acc

        # 2. Check keyword in category, target_audience or display_name
        for acc in accounts:
            searchable = f"{acc.category or ''} {acc.target_audience or ''} {acc.display_name or ''}"
            tokens = [t.strip() for t in re.split(r'[,/ ]+', searchable) if len(t.strip()) >= 2]
            if any(t in product_name for t in tokens):
                return acc

        # 3. Fallback to active accounts
        active_accs = [a for a in accounts if a.status == "ACTIVE"]
        return active_accs[0] if active_accs else accounts[0]