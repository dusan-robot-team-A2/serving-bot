import copy
from DTO import MenuItem, OrderTicket, TableInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget
from PyQt5.QtCore import QFile, QTextStream, Qt, QObject, pyqtSignal


class TableManager(QObject):
    table_update = pyqtSignal()
    
    def __init__(self, table:TableInfo=None):
        super().__init__()

        self.model = table

    def set_status(self, status:bool):
        if self.model.status != status:
            self.model.status = status
            self.table_update.emit()

    def set_order(self, order):
        if self.model.order != order:
            self.model.order = order
            self.table_update.emit()
    
    def update_table(self, table:TableInfo=None):
        if table:
            self.model = table
        self.table_update.emit()

class TicketManager(QObject):
    ticket_update = pyqtSignal()

    def __init__(self, ticket:OrderTicket=None):
        super().__init__()

        self.model = ticket
        self.is_disable = False

    def set_order(self, order):
        self.model.order = order
        self.update_ticket()
    
    def update_ticket(self):
        self.ticket_update.emit()
        print(self.model)

    def check_order(self):
        self.update_ticket()
    
    def check_all_order(self):
        is_all_checked = True
        for menu in self.model.order:
            if menu.is_checked == False:
                is_all_checked = False
                break
        
        for menu in self.model.order:
            if is_all_checked:
                menu.is_checked = False
            else:
                menu.is_checked = True
        self.update_ticket()
    
    def serve_checked_menus(self):
        is_all_menu_disable = True

        for menu in self.model.order:
            if menu.is_checked and not menu.is_disable:
                menu.is_disable = True
            
            if menu.is_disable == False:
                is_all_menu_disable = False
        
        if is_all_menu_disable:
            self.is_disable = True
        self.update_ticket()

    def get_is_checked_menu_and_table_id(self):
        if self.is_disable:
            return False, self.model.table_id

        for menu in self.model.order:
            if menu.is_checked and not menu.is_disable:
                return True, self.model.table_id
        
        return False, self.model.table_id

class DataManager(QObject):
    tables_update = pyqtSignal()
    tickets_update = pyqtSignal()
    robot_serve_update = pyqtSignal(int)#table id or home(0)


    def __init__(self, tables:list[TableInfo]=list(), tickets:list[OrderTicket]=list()):
        super().__init__()
        
        self.tables = [TableManager(table) for table in tables]
        self.tickets = [TicketManager(ticket) for ticket in tickets]

    def refresh_all(self):
        self.refresh_tables()
        self.refresh_tickets()

    def refresh_tables(self):
        self.tables_update.emit()
    
    def refresh_tickets(self):
        self.tickets_update.emit()
    
    def create_ticket(self, ticket: OrderTicket):
        for menu in ticket.order:
            menu.is_checked = False
            menu.is_disable = False
        self.tickets.insert(0, TicketManager(ticket))
        self.refresh_tickets()

    def create_order(self,ticket:OrderTicket):
        self.create_ticket(ticket)
        
        for table_manager in self.tables:
            if table_manager.model.table_id == ticket.table_id:
                new_ticket = copy.deepcopy(table_manager.model)
                new_ticket.order.extend(ticket.order)
                table_manager.update_table(new_ticket)

    def serve_checked_menu(self):
        for ticket_manager in self.tickets:
            ticket_manager.serve_checked_menus()
    
    def serve_checked_menu_by_robot(self):
        target_table_id = None
        for ticket_manager in self.tickets:
            is_checked_menu, table_id = ticket_manager.get_is_checked_menu_and_table_id()

            if is_checked_menu:
                if target_table_id is None:
                    target_table_id = table_id
                elif target_table_id != table_id:
                    print("같은 테이블의 항목으로 묶여 있어야 됩니다")
                    return
            
        if target_table_id is None:
            print("선택된 테이블이 없습니다")
        else:
            self.serve_checked_menu()
            self.control_robot(table_id)
    
    def call_robot(self):
        self.control_robot(0)

    def control_robot(self,table_id:int):
        print(f"contorl_robot: {table_id}로 이동명령")
        self.robot_serve_update.emit(table_id)
    


