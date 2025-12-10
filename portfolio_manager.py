"""
Portfolio Manager - إدارة المحافظ الشخصية ونسخ الروبوتات
"""
import json
import os
from datetime import datetime
from pathlib import Path

class PortfolioManager:
    def __init__(self):
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / 'portfolios.json'
        self.portfolios = self._load_portfolios()
    
    def _load_portfolios(self):
        """تحميل المحافظ من الملف"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_portfolios(self):
        """حفظ المحافظ إلى الملف"""
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolios, f, ensure_ascii=False, indent=2)
    
    def get_portfolio(self, user_id='default_user'):
        """الحصول على محفظة المستخدم"""
        if user_id not in self.portfolios:
            self.portfolios[user_id] = {
                'user_id': user_id,
                'total_balance': 0,
                'current_value': 0,
                'total_profit': 0,
                'profit_percent': 0,
                'copied_robots': [],
                'active_trades': 0,
                'completed_trades': 0,
                'success_rate': 0
            }
            self._save_portfolios()
        return self.portfolios[user_id]
    
    def add_robot(self, robot_id, robot_name, emoji, allocated_balance, user_id='default_user'):
        """إضافة روبوت للمحفظة"""
        portfolio = self.get_portfolio(user_id)
        
        # تحقق من عدم وجود الروبوت مسبقاً
        for robot in portfolio['copied_robots']:
            if robot['robot_id'] == robot_id:
                return {'success': False, 'message': 'الروبوت موجود بالفعل'}
        
        # إضافة الروبوت
        new_robot = {
            'robot_id': robot_id,
            'robot_name': robot_name,
            'emoji': emoji,
            'allocated_balance': allocated_balance,
            'current_balance': allocated_balance,
            'profit': 0,
            'profit_percent': 0,
            'active_trades': 0,
            'total_trades': 0,
            'success_rate': 0,
            'is_active': True,
            'copied_at': datetime.now().isoformat()
        }
        
        portfolio['copied_robots'].append(new_robot)
        portfolio['total_balance'] += allocated_balance
        portfolio['current_value'] += allocated_balance
        
        self._save_portfolios()
        return {'success': True, 'robot': new_robot}
    
    def remove_robot(self, robot_id, user_id='default_user'):
        """إزالة روبوت من المحفظة"""
        portfolio = self.get_portfolio(user_id)
        
        for i, robot in enumerate(portfolio['copied_robots']):
            if robot['robot_id'] == robot_id:
                removed_robot = portfolio['copied_robots'].pop(i)
                portfolio['total_balance'] -= removed_robot['allocated_balance']
                portfolio['current_value'] -= removed_robot['current_balance']
                self._save_portfolios()
                return {'success': True, 'message': 'تم إزالة الروبوت'}
        
        return {'success': False, 'message': 'الروبوت غير موجود'}
    
    def update_robot_balance(self, robot_id, new_balance, user_id='default_user'):
        """تحديث رصيد روبوت"""
        portfolio = self.get_portfolio(user_id)
        
        for robot in portfolio['copied_robots']:
            if robot['robot_id'] == robot_id:
                old_balance = robot['allocated_balance']
                robot['allocated_balance'] = new_balance
                
                # تحديث الرصيد الكلي
                portfolio['total_balance'] = portfolio['total_balance'] - old_balance + new_balance
                
                self._save_portfolios()
                return {'success': True, 'message': 'تم تحديث الرصيد'}
        
        return {'success': False, 'message': 'الروبوت غير موجود'}
    
    def update_robot_performance(self, robot_id, profit, active_trades, total_trades, user_id='default_user'):
        """تحديث أداء الروبوت"""
        portfolio = self.get_portfolio(user_id)
        
        for robot in portfolio['copied_robots']:
            if robot['robot_id'] == robot_id:
                robot['profit'] = profit
                robot['current_balance'] = robot['allocated_balance'] + profit
                robot['profit_percent'] = (profit / robot['allocated_balance'] * 100) if robot['allocated_balance'] > 0 else 0
                robot['active_trades'] = active_trades
                robot['total_trades'] = total_trades
                robot['success_rate'] = ((total_trades - active_trades) / total_trades * 100) if total_trades > 0 else 0
                
                # تحديث الإحصائيات الكلية
                self._update_portfolio_stats(user_id)
                self._save_portfolios()
                return {'success': True}
        
        return {'success': False, 'message': 'الروبوت غير موجود'}
    
    def _update_portfolio_stats(self, user_id='default_user'):
        """تحديث إحصائيات المحفظة الكلية"""
        portfolio = self.get_portfolio(user_id)
        
        total_balance = 0
        current_value = 0
        active_trades = 0
        total_trades = 0
        
        for robot in portfolio['copied_robots']:
            total_balance += robot['allocated_balance']
            current_value += robot['current_balance']
            active_trades += robot['active_trades']
            total_trades += robot['total_trades']
        
        portfolio['total_balance'] = total_balance
        portfolio['current_value'] = current_value
        portfolio['total_profit'] = current_value - total_balance
        portfolio['profit_percent'] = ((current_value - total_balance) / total_balance * 100) if total_balance > 0 else 0
        portfolio['active_trades'] = active_trades
        portfolio['completed_trades'] = total_trades - active_trades
        portfolio['success_rate'] = ((total_trades - active_trades) / total_trades * 100) if total_trades > 0 else 0
    
    def get_robot_performance(self, robot_id, user_id='default_user'):
        """الحصول على أداء روبوت معين"""
        portfolio = self.get_portfolio(user_id)
        
        for robot in portfolio['copied_robots']:
            if robot['robot_id'] == robot_id:
                return robot
        
        return None

# مثيل واحد للاستخدام في التطبيق
portfolio_manager = PortfolioManager()
