from flask import Flask, render_template, request, jsonify, flash, session, g
from app.database.connectDB import DatabaseConnectivity
from app.users.users_model import Users
from app.customers.customers_model import Customers
from app.engineers.engineers_models import Engineers
from app.workorders.work_orders_model import WorkOrders
from app.tickets.tickets_model import Tickets
from passlib.hash import sha256_crypt
import datetime
from datetime import timedelta
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)


dbInstance = DatabaseConnectivity()
usersInstance = Users()
custInstance = Customers()
engineersInstance = Engineers()
ordersInstance = WorkOrders()
ticketInstance = Tickets()

app = Flask(__name__)
app.secret_key = 'mysecretkeyghjngdssdfghjhdfhghhsffdtrdddvdvbggdsewwessaae'

app.config['JWT_SECRET_KEY'] = 'somesecretstuffsforjwt'
jwt = JWTManager(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

# @jwt.unauthorized_loader
# def unauthorized_response(callback):
#     return jsonify({
#         'Message': 'Missing Authorization Header'
#     }), 401

@app.before_request
def before_request():
    g.username = None
    if 'username' in session:
        g.username = session['username']


@app.route('/login')
def index():
    return render_template('index.html')

@app.route('/index', methods=['GET', 'POST'])
def login():
    session.pop('username', None)
    username = request.form['username']
    password_candidate = request.form['password']

    conn = dbInstance.connectToDatabase()
    cur =conn.cursor()
    result = cur.execute("SELECT user_name,user_password from users WHERE user_name=%s", [username])

    data = cur.fetchone()
    usernameDB = data[0]
    if usernameDB == username:
        password = data[1]
        if sha256_crypt.verify(password_candidate,password):
            session['username'] = username
            LoggedInUser = usersInstance.checkUserRights(username)
            allTheTickets = ticketInstance.view_all_tickets()
            myTickets = ticketInstance.view_all_tickets()
            return render_template('dashboard.html', allTheTickets=allTheTickets,currentUser=LoggedInUser,allMyTickets=myTickets)
            
        else:
            flash('Invalid Password', 'danger')
            return render_template('index.html')
    else:
        flash('{} is not registered'.format(username), 'danger')
        return render_template('index.html')

@app.route('/new_ticket')
def new_ticket():
    LoggedInUser = session['username']
    theClients = ticketInstance.get_clients()
    theEngineers = ticketInstance.get_engineers()
    theWorkOrderTypes = ticketInstance.get_work_order_types()
    return render_template('new_ticket.html',theWorkOrderTypes=theWorkOrderTypes, theEngineers=theEngineers, theClients=theClients,currentUser=LoggedInUser)

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    LoggedInUser = session['username']
    ticket_assigned_to = request.form['ticket_assigned_to']
    ticket_status =  request.form['ticket_status']
    hours_to_add = request.form['hours_to_add']
    ticket_opening_time = datetime.datetime.now()
    ticket_overdue_time =  datetime.datetime.now() + timedelta(hours=int(hours_to_add))
    ticket_client =  request.form['ticket_client']
    ticket_po_number = request.form['ticket_po_number']
    ticket_wo_type = request.form['ticket_wo_type']
    ticket_reason = request.form['ticket_reason']
    ticket_planned_visit_date = request.form['ticket_planned_visit_date']
    ticket_actual_visit_date = request.form['ticket_actual_visit_date']
    ticket_priority = request.form['ticket_priority']
    ticket_site_id = request.form['ticket_site_id']

    username = session['username']

    ticketInstance.add_ticket(ticket_assigned_to,ticket_opening_time,
    ticket_status,ticket_overdue_time,ticket_planned_visit_date,ticket_actual_visit_date,
    ticket_client,ticket_po_number,ticket_wo_type,ticket_reason,
    ticket_priority,username, ticket_site_id)
    theClients = ticketInstance.get_clients()
    theEngineers = ticketInstance.get_engineers()
    theWorkOrderTypes = ticketInstance.get_work_order_types()
    return render_template('new_ticket.html',theWorkOrderTypes=theWorkOrderTypes, theEngineers=theEngineers, theClients=theClients,currentUser=LoggedInUser)

@app.route('/edit_the_ticket/<int:ticket_id>', methods=['GET'])
def get_ticket_details_for_edit(ticket_id):
    LoggedInUser = session['username']
    theReturnedTicket = ticketInstance.get_ticket_by_Id(ticket_id)
    return render_template('edit_ticket.html', allTheTickets=theReturnedTicket,currentUser=LoggedInUser)


@app.route('/edit_ticket/<int:ticket_id>', methods=['POST'])
def edit_ticket(ticket_id):
    LoggedInUser = session['username']
    ticket_assigned_to = request.form['ticket_assigned_to_edit']
    ticket_status =  request.form['ticket_status_edit']
    hours_to_add = request.form['hours_to_add_edit']
    current_ticket_overdue_time = ticketInstance.get_ticket_overdue_time_by_Id(ticket_id)
    ticket_overdue_time =  current_ticket_overdue_time[0] + timedelta(hours=int(hours_to_add))
    ticket_client =  request.form['ticket_client_edit']
    ticket_po_number = request.form['ticket_po_number_edit']
    ticket_wo_type = request.form['ticket_wo_type_edit']
    ticket_reason = request.form['ticket_reason_edit']
    ticket_client_visit_note = "Just for test...no client visited site"
    ticket_planned_visit_date = request.form['ticket_planned_visit_date_edit']
    ticket_actual_visit_date = request.form['ticket_actual_visit_date_edit']
    ticket_priority = request.form['ticket_priority_edit']
    ticket_root_cause = request.form['ticket_root_cause_edit']
    ticket_action_taken = request.form['ticket_action_taken_edit']
    ticket_pending_reason = request.form['ticket_pending_reason_edit']
    ticket_additional_note = request.form['ticket_additional_note_edit']
    ticket_dispatch_time = request.form['ticket_dispatch_time']
    ticket_arrival_time = request.form['ticket_arrival_time']
    ticket_start_time = request.form['ticket_start_time']
    ticket_complete_time = request.form['ticket_complete_time']
    ticket_return_time = request.form['ticket_return_time']
    ticket_site_id = request.form['ticket_site_id_edit']
    if ticket_status == "Closed":
        ticket_closing_time = datetime.datetime.now()
    else:
        ticket_closing_time = None

    ticketInstance.edit_ticket(ticket_assigned_to,
    ticket_status,ticket_overdue_time,ticket_planned_visit_date,ticket_actual_visit_date,
    ticket_client,ticket_po_number,ticket_wo_type,ticket_reason,ticket_client_visit_note,
    ticket_priority,ticket_root_cause,
    ticket_action_taken,ticket_pending_reason,ticket_additional_note,ticket_site_id,ticket_closing_time,
    ticket_dispatch_time,ticket_arrival_time,ticket_start_time,ticket_complete_time,ticket_return_time,ticket_id)
    theClients = ticketInstance.get_clients()
    theEngineers = ticketInstance.get_engineers()
    theWorkOrderTypes = ticketInstance.get_work_order_types()
    return render_template('new_ticket.html',theWorkOrderTypes=theWorkOrderTypes, theEngineers=theEngineers, theClients=theClients,currentUser=LoggedInUser)


@app.route('/view_all_tickets', methods=['GET'])
def view_all_tickets():
    LoggedInUser = session['username']
    allTheTickets = ticketInstance.view_all_tickets()
    myTickets = ticketInstance.view_all_my_tickets(LoggedInUser)
    return render_template('dashboard.html', allTheTickets=allTheTickets, currentUser=LoggedInUser,myTickets=myTickets)

@app.route('/dashboard')
def dashboard():
    LoggedInUser = session['username']
    allTheTickets = ticketInstance.view_all_tickets()
    myTickets = ticketInstance.view_all_tickets()
    return render_template('dashboard.html', allTheTickets=allTheTickets, currentUser=LoggedInUser,myTickets=myTickets)


@app.route('/reports')
def reports():
    LoggedInUser = session['username']
    return render_template('reports.html', currentUser=LoggedInUser)

@app.route('/tasks')
def tasks():
    LoggedInUser = session['username']
    return render_template('tasks.html', currentUser=LoggedInUser)


@app.route('/client')
def new_customer():
    LoggedInUser = session['username']
    return render_template('new_customer.html', currentUser=LoggedInUser)

@app.route('/user')
def new_users():
    LoggedInUser = session['username']
    theReturnedUser = usersInstance.get_no_user()
    return render_template('new_users.html', allTheUsers=theReturnedUser,currentUser=LoggedInUser)

@app.route('/engineer')
def new_engineer():
    LoggedInUser = session['username']
    return render_template('new_engineer.html',currentUser=LoggedInUser)

@app.route('/equipment')
def new_equipment():
    LoggedInUser = session['username']
    return render_template('new_equipment.html',currentUser=LoggedInUser)

@app.route('/workorder')
def new_workorder():
    LoggedInUser = session['username']
    return render_template('new_workorder.html',currentUser=LoggedInUser)

@app.route('/add_user', methods=['POST'])
def add_user():
    LoggedInUser = session['username']
    firstName = request.form['user_first_name']
    lastName = request.form['user_last_name']
    userName = request.form['user_name']
    email = request.form['user_email']
    userAddress = request.form['user_physical_address']
    userPhone = request.form['user_phone']
    userPassword = request.form['user_password']
    can_add_user = request.form.get('can_add_user')
    if can_add_user:
        can_add_user_value = 1
    else:
        can_add_user_value = 0

    can_delete_user = request.form.get('can_delete_user')
    if can_delete_user:
        can_delete_user_value = 1
    else:
        can_delete_user_value = 0

    can_edit_user = request.form.get('can_edit_user')
    if can_edit_user:
        can_edit_user_value = 1
    else:
        can_edit_user_value = 0

    can_edit_his_info = request.form.get('can_edit_his_info')
    if can_edit_his_info:
        can_edit_his_info_value = 1
    else:
        can_edit_his_info_value = 0

    can_open_tickets = request.form.get('can_open_tickets')
    if can_open_tickets:
        can_open_tickets_value = 1
    else:
        can_open_tickets_value = 0

    can_edit_tickets = request.form.get('can_edit_tickets')
    if can_edit_tickets:
        can_edit_tickets_value = 1
    else:
        can_edit_tickets_value = 0

    can_delete_tickets = request.form.get('can_delete_tickets')
    if can_delete_tickets:
        can_delete_tickets_value = 1
    else:
        can_delete_tickets_value = 0

    can_view_all_tickets = request.form.get('can_view_all_tickets')
    if can_view_all_tickets:
        can_view_all_tickets_value = 1
    else:
        can_view_all_tickets_value = 0

    can_view_his_tickets = request.form.get('can_view_his_tickets')
    if can_view_his_tickets:
        can_view_his_tickets_value = 1
    else:
        can_view_his_tickets_value = 0

    can_edit_his_tickets = request.form.get('can_edit_his_tickets')
    if can_edit_his_tickets:
        can_edit_his_tickets_value = 1
    else:
        can_edit_his_tickets_value = 0

    can_view_his_tasks = request.form.get('can_view_his_tasks')
    if can_view_his_tasks:
        can_view_his_tasks_value = 1
    else:
        can_view_his_tasks_value = 0

    can_view_all_tasks = request.form.get('can_view_all_tasks')
    if can_view_all_tasks:
        can_view_all_tasks_value = 1
    else:
        can_view_all_tasks_value = 0

    can_view_his_reports = request.form.get('can_view_his_reports')
    if can_view_his_reports:
        can_view_his_reports_value = 1
    else:
        can_view_his_reports_value = 0

    can_view_all_reports = request.form.get('can_view_all_reports')
    if can_view_all_reports:
        can_view_all_reports_value = 1
    else:
        can_view_all_reports_value = 0

    can_add_delete_edit_client = request.form.get('can_add_delete_edit_clients')
    if can_add_delete_edit_client:
        can_add_delete_edit_client_value = 1
    else:
        can_add_delete_edit_client_value = 0

    can_add_delete_edit_engineer = request.form.get('can_add_delete_edit_engineers')
    if can_add_delete_edit_engineer:
        can_add_delete_edit_engineer_value = 1
    else:
        can_add_delete_edit_engineer_value = 0


    can_add_delete_edit_equipment = request.form.get('can_add_delete_edit_equipment')
    if can_add_delete_edit_equipment:
        can_add_delete_edit_equipment_value = 1
    else:
        can_add_delete_edit_equipment_value = 0


    can_add_delete_edit_workorder = request.form.get('can_add_delete_edit_workorder')
    if can_add_delete_edit_workorder:
        can_add_delete_edit_workorder_value = 1
    else:
        can_add_delete_edit_workorder_value = 0

    encryptedPassword = sha256_crypt.encrypt(str(userPassword))
    usersInstance.add_user(firstName,lastName,email,userAddress,userPhone,userName,encryptedPassword,
    can_add_user_value,can_delete_user_value,can_edit_user_value,can_edit_his_info_value,
    can_open_tickets_value,can_edit_tickets_value,can_delete_tickets_value,can_view_all_tickets_value,
    can_view_his_tickets_value,can_edit_his_tickets_value,can_view_his_tasks_value,can_view_all_tasks_value,
    can_view_his_reports_value,can_view_all_reports_value,can_add_delete_edit_client_value,
    can_add_delete_edit_engineer_value,can_add_delete_edit_equipment_value,can_add_delete_edit_workorder_value)
    theReturnedUsers = usersInstance.view_all_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

@app.route('/add_client', methods=['POST'])
def add_client():
    LoggedInUser = session['username']
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    customer_phone = request.form['customer_phone']
    customer_address = request.form['customer_address']
    customer_product = request.form['customer_product']
    custInstance.add_client(customer_name,customer_phone,customer_email,customer_address,customer_product)
    return render_template('new_customer.html',currentUser=LoggedInUser)

@app.route('/add_engineer', methods=['POST'])
def add_engineer():
    LoggedInUser = session['username']
    engineer_first_name = request.form['engineer_first_name']
    engineer_last_name = request.form['engineer_last_name']
    engineer_email = request.form['engineer_email']
    engineer_phone = request.form['engineer_phone']
    engineer_address = request.form['engineer_address']
    engineer_field_ATM = request.form.get('engineer_field_ATM')
    if engineer_field_ATM:
        engineer_field_ATM_Value = 1
    else:
        engineer_field_ATM_Value = 0

    engineer_field_AIR = request.form.get('engineer_field_AIR')
    if engineer_field_AIR:
        engineer_field_AIR_Value = 1
    else:
        engineer_field_AIR_Value = 0

    engineer_field_TEL = request.form.get('engineer_field_TEL')
    if engineer_field_TEL:
        engineer_field_TEL_Value = 1
    else:
        engineer_field_TEL_Value = 0

    engineersInstance.add_engineer(engineer_first_name,engineer_last_name,engineer_phone,engineer_email,engineer_address,engineer_field_ATM_Value,engineer_field_AIR_Value,engineer_field_TEL_Value)
    return render_template('new_engineer.html',currentUser=LoggedInUser)


@app.route('/all_users', methods=['GET'])
def all_users():
    LoggedInUser = session['username']
    theReturnedUsers = usersInstance.view_all_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

@app.route('/all_admin_users', methods=['GET'])
def all_admin_users():
    LoggedInUser = session['username']
    theReturnedUsers = usersInstance.view_all_admin_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

@app.route('/all_ordinary_users', methods=['GET'])
def all_ordinary_users():
    LoggedInUser = session['username']
    theReturnedUsers = usersInstance.view_all_ordinary_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

@app.route('/all_the_users/<int:user_id>', methods=['GET','DELETE'])
def delete_user(user_id):
    LoggedInUser = session['username']
    usersInstance.delete_a_user(user_id)
    theReturnedUsers = usersInstance.view_all_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

@app.route('/the_user/<int:user_id>', methods=['GET'])
def get_user_by_Id(user_id):
    LoggedInUser = session['username']
    theReturnedUser = usersInstance.get_user_by_Id(user_id)
    return render_template('new_users.html', allTheUsers=theReturnedUser,currentUser=LoggedInUser)

@app.route('/edit_the_user/<int:user_id>', methods=['GET'])
def get_user_details_for_edit(user_id):
    LoggedInUser = session['username']
    theReturnedUser = usersInstance.get_user_by_Id(user_id)
    return render_template('edit_user.html', allTheUsers=theReturnedUser,currentUser=LoggedInUser)

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    LoggedInUser = session['username']
    firstName = request.form['user_first_name_edit']
    lastName = request.form['user_last_name_edit']
    userName = request.form['user_name_edit']
    email = request.form['user_email_edit']
    userAddress = request.form['user_address_edit']
    userPhone = request.form['user_phone_edit']
    userPassword = request.form['user_password_edit']


    can_add_user = request.form.get('can_add_user_edit')
    if can_add_user:
        can_add_user_value = 1
    else:
        can_add_user_value = 0

    can_delete_user = request.form.get('can_delete_user_edit')
    if can_delete_user:
        can_delete_user_value = 1
    else:
        can_delete_user_value = 0

    can_edit_user = request.form.get('can_edit_user_edit')
    if can_edit_user:
        can_edit_user_value = 1
    else:
        can_edit_user_value = 0

    can_edit_his_info = request.form.get('can_edit_his_info_edit')
    if can_edit_his_info:
        can_edit_his_info_value = 1
    else:
        can_edit_his_info_value = 0

    can_open_tickets = request.form.get('can_open_tickets_edit')
    if can_open_tickets:
        can_open_tickets_value = 1
    else:
        can_open_tickets_value = 0

    can_edit_tickets = request.form.get('can_edit_tickets_edit')
    if can_edit_tickets:
        can_edit_tickets_value = 1
    else:
        can_edit_tickets_value = 0

    can_delete_tickets = request.form.get('can_delete_tickets_edit')
    if can_delete_tickets:
        can_delete_tickets_value = 1
    else:
        can_delete_tickets_value = 0

    can_view_all_tickets = request.form.get('can_view_all_tickets_edit')
    if can_view_all_tickets:
        can_view_all_tickets_value = 1
    else:
        can_view_all_tickets_value = 0

    can_view_his_tickets = request.form.get('can_view_his_tickets_edit')
    if can_view_his_tickets:
        can_view_his_tickets_value = 1
    else:
        can_view_his_tickets_value = 0

    can_edit_his_tickets = request.form.get('can_edit_his_tickets_edit')
    if can_edit_his_tickets:
        can_edit_his_tickets_value = 1
    else:
        can_edit_his_tickets_value = 0

    can_view_his_tasks = request.form.get('can_view_his_tasks_edit')
    if can_view_his_tasks:
        can_view_his_tasks_value = 1
    else:
        can_view_his_tasks_value = 0

    can_view_all_tasks = request.form.get('can_view_all_tasks_edit')
    if can_view_all_tasks:
        can_view_all_tasks_value = 1
    else:
        can_view_all_tasks_value = 0

    can_view_his_reports = request.form.get('can_view_his_reports_edit')
    if can_view_his_reports:
        can_view_his_reports_value = 1
    else:
        can_view_his_reports_value = 0

    can_view_all_reports = request.form.get('can_view_all_reports_edit')
    if can_view_all_reports:
        can_view_all_reports_value = 1
    else:
        can_view_all_reports_value = 0

    can_add_delete_edit_client = request.form.get('can_add_delete_edit_clients_edit')
    if can_add_delete_edit_client:
        can_add_delete_edit_client_value = 1
    else:
        can_add_delete_edit_client_value = 0

    can_add_delete_edit_engineer = request.form.get('can_add_delete_edit_engineers_edit')
    if can_add_delete_edit_engineer:
        can_add_delete_edit_engineer_value = 1
    else:
        can_add_delete_edit_engineer_value = 0


    can_add_delete_edit_equipment = request.form.get('can_add_delete_edit_equipment_edit')
    if can_add_delete_edit_equipment:
        can_add_delete_edit_equipment_value = 1
    else:
        can_add_delete_edit_equipment_value = 0


    can_add_delete_edit_workorder = request.form.get('can_add_delete_edit_workorder_edit')
    if can_add_delete_edit_workorder:
        can_add_delete_edit_workorder_value = 1
    else:
        can_add_delete_edit_workorder_value = 0

    encryptedPassword = sha256_crypt.encrypt(str(userPassword))
    usersInstance.edit_a_user(user_id,firstName, lastName,email,userPhone,userAddress,userName,encryptedPassword,
    can_add_user_value,can_delete_user_value,can_edit_user_value,can_edit_his_info_value,
    can_open_tickets_value,can_edit_tickets_value,can_delete_tickets_value,can_view_all_tickets_value,
    can_view_his_tickets_value,can_edit_his_tickets_value,can_view_his_tasks_value,can_view_all_tasks_value,
    can_view_his_reports_value,can_view_all_reports_value,can_add_delete_edit_client_value,
    can_add_delete_edit_engineer_value,can_add_delete_edit_equipment_value,can_add_delete_edit_workorder_value)
    theReturnedUsers = usersInstance.view_all_users()
    return render_template('view_users.html', allTheUsers=theReturnedUsers,currentUser=LoggedInUser)

# WORK ORDERS

@app.route('/edit_the_work_order/<int:work_order_id>', methods=['GET'])
def edit_the_work_order(work_order_id):
    LoggedInUser = session['username']
    theReturnedOrder = ordersInstance.get_work_order_by_Id(work_order_id)
    return render_template('edit_work_order.html', allTheOrders=theReturnedOrder,currentUser=LoggedInUser)

@app.route('/add_work_order', methods=['POST'])
def add_work_order():
    LoggedInUser = session['username']
    work_order_type = request.form['work_order_type']
    ordersInstance.add_work_order(work_order_type)
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

@app.route('/edit_the_work_order/<int:work_order_id>', methods=['POST'])
def edit_work_order(work_order_id):
    LoggedInUser = session['username']
    workOrderType = request.form['work_order_type_edit']
    ordersInstance.edit_a_work_order(work_order_id,workOrderType)
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

@app.route('/all_the_work_orders/<int:work_order_id>', methods=['GET','DELETE'])
def delete_work_order(work_order_id):
    LoggedInUser = session['username']
    ordersInstance.delete_a_work_order(work_order_id)
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

@app.route('/all_work_orders', methods=['GET'])
def all_work_orders():
    LoggedInUser = session['username']
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

@app.route('/all_work_orders_completed', methods=['GET'])
def all_work_orders_completed():
    LoggedInUser = session['username']
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

@app.route('/all_work_orders_pending', methods=['GET'])
def all_work_orders_pending():
    LoggedInUser = session['username']
    theReturnedOrders = ordersInstance.view_all_work_orders()
    return render_template('view_work_order.html', allTheOrders=theReturnedOrders,currentUser=LoggedInUser)

# OUR CLIENTS

@app.route('/all_clients', methods=['GET'])
def all_clients():
    LoggedInUser = session['username']
    theReturnedClients = custInstance.get_all_clients()
    return render_template('view_clients.html', allTheClients=theReturnedClients,currentUser=LoggedInUser)

@app.route('/all_the_clients/<int:client_id>', methods=['GET','DELETE'])
def delete_client(client_id):
    LoggedInUser = session['username']
    custInstance.delete_a_client(client_id)
    theReturnedClients = custInstance.get_all_clients()
    return render_template('view_clients.html', allTheClients=theReturnedClients,currentUser=LoggedInUser)

@app.route('/the_client/<int:client_id>', methods=['GET'])
def get_client_by_Id(client_id):
    LoggedInUser = session['username']
    theReturnedClient = custInstance.get_client_by_Id(client_id)
    return render_template('new_customer.html', allTheClients=theReturnedClient,currentUser=LoggedInUser)

@app.route('/edit_the_client/<int:client_id>', methods=['GET'])
def get_client_details_for_edit(client_id):
    LoggedInUser = session['username']
    theReturnedClient = custInstance.get_client_by_Id(client_id)
    return render_template('edit_client.html', allTheClients=theReturnedClient,currentUser=LoggedInUser)

@app.route('/edit_client/<int:client_id>', methods=['POST'])
def edit_client(client_id):
    LoggedInUser = session['username']
    clientName = request.form['customer_name_edit']
    clientProduct = request.form['customer_product_edit']
    clientAddress = request.form['customer_address_edit']
    clientPhone = request.form['customer_phone_edit']
    clientEmail = request.form['customer_email_edit']
   
    custInstance.edit_a_client(client_id,clientName, clientProduct,clientAddress,clientPhone,clientEmail)
    theReturnedClients = custInstance.get_all_clients()
    return render_template('view_clients.html', allTheClients=theReturnedClients,currentUser=LoggedInUser)

# OUR ENGINEERS

@app.route('/all_engineers', methods=['GET'])
def all_engineers():
    LoggedInUser = session['username']
    theReturnedEngineers = engineersInstance.get_all_engineers()
    return render_template('view_engineers.html', allTheEngineers=theReturnedEngineers,currentUser=LoggedInUser)

@app.route('/all_the_engineers/<int:engineer_id>', methods=['GET','DELETE'])
def delete_engineer(engineer_id):
    LoggedInUser = session['username']
    engineersInstance.delete_a_engineer(engineer_id)
    theReturnedEngineers = engineersInstance.get_all_engineers()
    return render_template('view_engineers.html', allTheEngineers=theReturnedEngineers,currentUser=LoggedInUser)

@app.route('/the_engineer/<int:engineer_id>', methods=['GET'])
def get_engineer_by_Id(engineer_id):
    LoggedInUser = session['username']
    theReturnedEngineer = engineersInstance.get_engineer_by_Id(engineer_id)
    return render_template('new_engineer.html', allTheEngineers=theReturnedEngineer,currentUser=LoggedInUser)

@app.route('/edit_the_engineer/<int:engineer_id>', methods=['GET'])
def get_engineer_details_for_edit(engineer_id):
    LoggedInUser = session['username']
    theReturnedEngineer = engineersInstance.get_engineer_by_Id(engineer_id)
    return render_template('edit_engineer.html', allTheEngineers=theReturnedEngineer,currentUser=LoggedInUser)

@app.route('/edit_engineer/<int:engineer_id>', methods=['POST'])
def edit_engineer(engineer_id):
    LoggedInUser = session['username']
    engineer_first_name = request.form['engineer_first_name_edit']
    engineer_last_name = request.form['engineer_last_name_edit']
    engineer_email = request.form['engineer_email_edit']
    engineer_phone = request.form['engineer_phone_edit']
    engineer_address = request.form['engineer_address_edit']
    engineer_field_ATM = request.form.get('engineer_field_ATM_edit')
    if engineer_field_ATM:
        engineer_field_ATM_Value = 1
    else:
        engineer_field_ATM_Value = 0

    engineer_field_AIR = request.form.get('engineer_field_AIR_edit')
    if engineer_field_AIR:
        engineer_field_AIR_Value = 1
    else:
        engineer_field_AIR_Value = 0

    engineer_field_TEL = request.form.get('engineer_field_TEL_edit')
    if engineer_field_TEL:
        engineer_field_TEL_Value = 1
    else:
        engineer_field_TEL_Value = 0

    engineersInstance.edit_an_engineer(engineer_id,engineer_first_name,engineer_last_name,engineer_address,engineer_phone,engineer_email,engineer_field_ATM_Value,engineer_field_AIR_Value,engineer_field_TEL_Value)
    theReturnedEngineers = engineersInstance.get_all_engineers()
    return render_template('view_engineers.html', allTheEngineers=theReturnedEngineers,currentUser=LoggedInUser)
