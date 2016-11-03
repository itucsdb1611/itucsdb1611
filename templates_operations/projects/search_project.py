from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from datetime import datetime
from datetime import datetime
from classes.operations.project_operations import project_operations
from classes.project import Project


def project_search_page_config(submit_type):
    store = project_operations()
    if submit_type=='GET':
        projects = store.get_projects()
        return render_template('projects/search_project.html', projects=projects)
    else:
        if 'check' and 'delete' in request.form:
            keys = request.form.getlist('check')
            for key in keys:
                store.delete_project(int(key))
            return render_template('dashboard.html')
 #       elif 'check' and 'update' in request.form:
 #           key = request.form.getlist('check')
 #           project = store.get_project(int(key))
 #           return redirect(url_for('site.projects_details_page'), projects = project)
         #   return render_template('projects/project_detail.html', projects= project)

