from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import enum


class Inmate(db.Model):
    inmate_id = db.Column(db.Integer, primary_key=True)
    mess_no = db.Column(db.Integer, unique=True, nullable=False)
    inmate_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    is_ablc = db.Column(db.Boolean, nullable=False, default=True)
    join_date = db.Column(db.DateTime, nullable=False, default=func.current_date)
    last_edit = db.Column(db.DateTime, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # is_bill_due = db.Column(db.Boolean, default=False)
    is_bill_due = db.Column(db.Integer, default=0)
    image = db.Column(db.String(150), default='unknown.jpg')


class UserActiveStatus(enum.Enum):
    ACTIVE = 'Active'
    SUSPENDED = 'Suspended'
    TERMINATED = 'Terminated'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    user_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    added_date = db.Column(db.DateTime, nullable=False, default=func.now)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    active_status = db.Column(db.Enum(UserActiveStatus), nullable=False, default=UserActiveStatus.ACTIVE)
    role = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(300), default='images/users/default.jpg')


class MessStatus(db.Model):
    inmate_id = db.Column(db.Integer, db.ForeignKey('inmate.inmate_id'))
    update_date = db.Column(db.DateTime, nullable=False, default=func.current_date)
    in_status = db.Column(db.Boolean, nullable=False, default=False)
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Set composite primary key (inmate_id and update_date)
    __table_args__ = (db.PrimaryKeyConstraint('inmate_id', 'update_date'),)


class MealsLog(db.Model):
    inmate_id = db.Column(db.Integer, db.ForeignKey('inmate.inmate_id'))
    update_date = db.Column(db.DateTime, nullable=False, default=func.current_date)
    breakfast = db.Column(db.Boolean, default=False)
    lunch = db.Column(db.Boolean, default=False)
    dinner = db.Column(db.Boolean, default=False)
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Set composite primary key (inmate_id and update_date)
    __table_args__ = (db.PrimaryKeyConstraint('inmate_id', 'update_date'),)


class GuestLog(db.Model):
    inmate_id = db.Column(db.Integer, db.ForeignKey('inmate.inmate_id'))
    update_date = db.Column(db.DateTime, nullable=False, default=func.current_date)
    guest_count = db.Column(db.Integer)
    sg_count = db.Column(db.Integer)
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Set composite primary key (inmate_id and update_date)
    __table_args__ = (db.PrimaryKeyConstraint('inmate_id', 'update_date'),)


class MonthlyBillInfo(db.Model):
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    guest_amount = db.Column(db.Integer, nullable=False)  # Fixed amount for guest and SG
    opening_stock = db.Column(db.Integer, nullable=False)
    closing_stock = db.Column(db.Integer, nullable=False)
    vacated_amount_fixed = db.Column(db.Integer)
    vacated_amount_daily = db.Column(db.Integer)
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Set composite primary key (inmate_id and update_date)
    __table_args__ = (db.PrimaryKeyConstraint('year', 'month'),)


class ExpenseEnum(enum.Enum):
    FIXED = "Fixed"
    PURCHASE = "Purchase"


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(150))
    bill_date = db.Column(db.DateTime, nullable=False, default=func.current_date)
    shop = db.Column(db.String(50))
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Enum(ExpenseEnum), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    last_edit = db.Column(db.DateTime, nullable=False, default=func.now)
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Bill(db.Model):
    inmate_id = db.Column(db.Integer, db.ForeignKey('inmate.inmate_id'))
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Unpaid')
    generated_date = db.Column(db.DateTime, default=func.now)
    reference_id = db.Column(db.String(50))
    paid_date = db.Column(db.Date)
    __table_args__ = (db.PrimaryKeyConstraint('inmate_id', 'year', 'month'),)


class StatusInitializationLog(db.Model):
    __tablename__ = 'status_initialization_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    initialized_at = db.Column(db.DateTime, default=func.now)


class BillsGenerated(db.Model):
    __tablename__ = 'bills_generated'
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    is_generated = db.Column(db.Boolean, default=False)
    __table_args__ = (db.PrimaryKeyConstraint('year', 'month'),)