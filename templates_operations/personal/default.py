from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from datetime import datetime
from flask_login import current_user, login_required
from classes.operations.person_operations import person_operations
from classes.operations.project_operations import project_operations
from classes.operations.followed_person_operations import followed_person_operations
from classes.operations.personComment_operations import personComment_operations
from classes.look_up_tables import *
from classes.person import Person
from classes.operations.followed_project_operations import followed_project_operations
from classes.followed_project import FollowedProject
from classes.operations.team_operations import team_operations
from classes.operations.education_operations import education_operations
from classes.operations.skill_operations import skill_operations
from classes.operations.Experience_operations import experience_operations
from classes.operations.information_operations import information_operations
from classes.operations.language_operations import language_operations
from classes.operations.CV_operations import cv_operations

import os
from werkzeug.utils import secure_filename
from passlib.apps import custom_app_context as pwd_context
from templates_operations.user import*

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def personal_default_page_config(request):
    PersonProvider = person_operations()
    Current_Person = PersonProvider.GetPerson(current_user.email)
    comments = personComment_operations()
    store_followed_projects = followed_project_operations()
    EducationProvider = education_operations()
    SkillProvider = skill_operations()
    InformationProvider = information_operations()
    LanguageProvider = language_operations()
    TeamProvider = team_operations()
    if request and 'delete' in request.form and request.method == 'POST':
        p = PersonProvider.GetPersonByObjectId(request.form['delete'])
        PersonProvider.DeletePerson(request.form['delete'])
    if request and 'deleteComment' in request.form and request.method == 'POST':
        comments.DeleteTeam(request.form['deleteComment'])
    elif request and 'updateComment' in request.form and request.method == 'POST':
        selectedComment = request.form['updateId']
        updatedComment = request.form['updateComment']
        comments.UpdatePersonComment(selectedComment, updatedComment)
    elif request and 'addComment' in request.form and request.method == 'POST':
        personId = Current_Person[0]
        commentedPersonId = Current_Person[0]
        newComment = request.form['addComment']
        comments.AddPersonComment(personId, commentedPersonId, newComment)
    elif 'unfollowProject' in request.form:
        project_id = request.form['unfollowProject']
        store_followed_projects.DeleteFollowedProject(project_id)
    elif request and 'searchPeoplePage' in request.form and request.method == 'POST':
        return redirect(url_for('site.people_search_person_page'))
    elif request and 'searchProjectPage' in request.form and request.method == 'POST':
        return redirect(url_for('site.projects_search_page'))
    elif request and 'saveProfileSettings' in request.form and request.method == 'POST':
        FollowedPersonProvider = followed_person_operations()
        listFollowing = FollowedPersonProvider.GetFollowedPersonListByPersonId(Current_Person[0])
        listFollowers = FollowedPersonProvider.GetFollowedPersonListByFollowedPersonId(Current_Person[0])
        personComments = comments.GetPersonCommentsByCommentedPersonId(Current_Person[0])
        listTitle = GetTitleList()
        listAccount = GetAccountTypeList()
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        pswd = request.form['pswd']
        accountType = request.form['account']
        title = request.form['title']
        file = request.files['file']
        gender = request.form['r1']
        if gender == 'male':
            gender = False
        elif gender == 'female':
            gender = True
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename != Current_Person[7]:
                file.save(os.path.join('static/user_images', filename))
            else:
                filename = Current_Person[7]
        elif Current_Person[7] is None:
            if gender:
                filename = 'noimage_female.jpg'
            else:
               filename = 'noimage_male.jpg'
        else:
            filename = Current_Person[7]
        if pswd != "":
            pswd = pwd_context.encrypt(request.form['pswd'])
            UpdateUser(pswd, current_user.email)
        PersonProvider.UpdatePerson(Current_Person[0], first_name, last_name, accountType, ' ', gender, title, filename, False)
        return redirect(url_for('site.personal_default_page', Current_Person=Current_Person,
                            listFollowing=listFollowing, listFollowers=listFollowers,
                            personComments=personComments, listAccount=listAccount, listTitle=listTitle))
    FollowedPersonProvider = followed_person_operations()
    listFollowing = FollowedPersonProvider.GetFollowedPersonListByPersonId(Current_Person[0])
    listFollowers = FollowedPersonProvider.GetFollowedPersonListByFollowedPersonId(Current_Person[0])
    personComments = comments.GetPersonCommentsByCommentedPersonId(Current_Person[0])
    followed_projects = store_followed_projects.GetFollowedProjectListByPersonId(Current_Person[0])
    count = 0
    while (count < len(followed_projects)):
        temp = list(followed_projects[count])
        temp.append(list(TeamProvider.GetAllMembersByProjectId(followed_projects[count][8])))
        temp.append(len(store_followed_projects.GetFollowerPersonListByFollowedProjectId(followed_projects[count][8])))
        followed_projects[count] = tuple(temp)
        count = count + 1
    now = datetime.datetime.now()
    listTitle = GetTitleList()
    listAccount = GetAccountTypeList()
    store_projects = project_operations()
    active_projects = store_projects.get_the_projects_of_a_person(Current_Person[0])
    count = 0
    while (count < len(active_projects)):
        temp = list(active_projects[count])
        temp.append(list(TeamProvider.GetAllMembersByProjectId(active_projects[count][3])))
        temp.append(len(store_followed_projects.GetFollowerPersonListByFollowedProjectId(active_projects[count][3])))
        active_projects[count] = tuple(temp)
        count = count + 1
    active_project_number = len(active_projects)
    listEducation = EducationProvider.GetEducationListByActiveCVAndByPersonId(Current_Person[0])
    listSkill = SkillProvider.GetSkillByActiveCVAndByPersonId(Current_Person[0])
    listLanguage = LanguageProvider.GetAllLanguagesByActiveCVAndByPersonId(Current_Person[0])
    listInformation = InformationProvider.get_all_information_by_ActiveCV_And_PersonId(Current_Person[0])
    CvProvider = cv_operations()
    activeCv = CvProvider.get_active_cv(Current_Person[0])
    ExperienceProvider=experience_operations()
    if activeCv:
        listExperience = ExperienceProvider.get_experiences_with_key(activeCv[0])
    else:
        listExperience = 'none'
    return render_template('personal/default.html', current_time=now.ctime(), Current_Person=Current_Person,
                           listFollowing=listFollowing, listFollowers=listFollowers, followed_projects=followed_projects,
                           personComments=personComments, listAccount=listAccount, listTitle=listTitle,
                           active_projects=active_projects, active_project_number=active_project_number,listEducation=listEducation, listSkill=listSkill,
                           listExperience=listExperience, listLanguage=listLanguage, listInformation=listInformation)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
# if submit_type == 'GET':
#    store = followed_person_operations()
# result = store.GetFollowedPersonByObjectId(2)
#    result = store.GetFollowedPersonList()
# p = FollowedPerson(None, 1, 2, datetime.now())
# store.AddFollowedPerson(p)
#    now = datetime.now()
#    return render_template('personal/default.html', current_time=now.ctime(), FollowedPersonList=result)
# from classes.operations.followed_person_operations import followed_person_operations
# from classes.followed_person import FollowedPerson
