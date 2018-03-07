from flask import render_template, request, url_for, make_response, jsonify, Blueprint
from flask_login import login_required

# Initialize the Flask application
app = Blueprint('app', __name__, template_folder='./templates', static_folder='./static', static_url_path = 'static/')

@app.route("style.css")
def css():
    response = make_response(render_template("inv_style.css"))
    return response

#Custom error
#Does not appear in routings
class BadNameError(KeyError):
    """Raise when there is a problem"""
    def __init__(self, message):
        mess = "Requested name does not exist"
        super(KeyError, self).__init__(mess)

#The root
@app.route('')
def show_root():
    return render_template('template.html')

@app.route('<string:id>/')
def show_child(id):
    return render_template('template2.html')

@app.route('<string:id>/<string:id2>/')
def show_next_child(id, id2):
    return render_template('template3.html')

@app.route('<string:id>/<string:id2>/facts/')
def show_facts(id, id2):
    return render_template('view_facts.html')

@app.route('<string:id>/<string:id2>/things/')
def show_things(id, id2):
    return render_template('view_things.html')

@app.route('<string:id>/<string:id2>/edit/')
@login_required
def show_edit(id, id2):
    return render_template('edit.html')

@app.route('<string:id>/<string:id2>/facts/edit/')
@login_required
def show_edit_facts(id, id2):
    return render_template('edit_facts.html')

#-------- Data sources (json returns) ----------------------------------------

@app.route('live/')
def generate_live_list():
    results = get_json_live()
    return jsonify(results)

#Data source to populate pages
@app.route('<string:id>/<string:id2>/edit/data/')
@app.route('<string:id>/<string:id2>/data/')
def fetch_data(id, id2):
    results = get_data(id, id2)
    return jsonify(results)

#Data source to populate facts pages
@app.route('<string:id>/<string:id2>/facts/data/')
@app.route('<string:id>/<string:id2>/facts/edit/data/')
def fetch_facts(id, id2):
    results = get_facts(id, id2)
    return jsonify(results)

#Data source to populate things pages
@app.route('<string:id>/<string:id2>/things/data/')
def fetch_things(id, id2):
    results = get_things(id, id2)
    return jsonify(results)

#Page shown after successful edit submission
@app.route('success/')
def edit_success(request=request):
    return render_template('edit_success.html')

#Page shown after failing edits
@app.route('failure/', methods=['GET'])
def edit_failure(request=request):
    return render_template('edit_failure.html')

#Destination for edit submissions
@app.route('submit/', methods=['POST'])
@login_required
def submit_edits():
    #Return a redirect to be done on client
    return jsonify({'url':url_for('app.edit_success'), 'code':302, 'success':True})

@app.route('process/')
@login_required
def show_process_page():
    return render_template('process.html')

@app.route('process/<string:id>/<string:id2>')
def fetch_process_things(id, id2):
    return render_template('progress.html', things={'id':id, 'id2':id2})

@app.route('process/progress/<string:uid>/')
@login_required
def show_progress(uid):
    return render_template('progress.html')

@app.route('process/progress/<string:uid>/monitor/')
@login_required
def fetch_progress_data(uid):
    progress = get_progress(uid)
    return jsonify(progress)

@app.route('process/submit/', methods=['POST'])
@login_required
def submit_request():
    return jsonify({'url':url_for('app.request_process')})

@app.route('controlpanel/')
@login_required
def show_panel():
    return render_template('control_panel.html')

@app.route('controlpanel/trigger/', methods=['POST'])
@login_required
def trigger_control_functions():
    outcome = act(request.data)
    return jsonify(outcome)
