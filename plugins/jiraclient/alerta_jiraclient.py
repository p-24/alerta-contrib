import os
import datetime
from jira import JIRA
import logging

#try:
#    from alerta.plugins import app  # alerta >= 5.0
#except ImportError:
#    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.jira')


#JIRA_API_URL = os.environ.get('JIRA_API_URL') or app.config.get('JIRA_API_URL', None)
#JIRA_API_USERNAME = os.environ.get('JIRA_API_USERNAME') or app.config.get('JIRA_API_USERNAME', '')
#JIRA_API_PASSWORD = os.environ.get('JIRA_API_PASSWORD') or app.config.get('JIRA_API_PASSWORD', '')
#JIRA_PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY') or app.config.get('JIRA_PROJECT_KEY', '')
#JIRA_ISSUE_TYPE =  os.environ.get('JIRA_ISSUE_TYPE') or app.config.get('JIRA_ISSUE_TYPE', 'Bug')

JIRA_API_URL = 'http://uat-servicedesk.nvidiangn.net:8080'
JIRA_API_USERNAME = 'moogqa'
JIRA_API_PASSWORD = 'moogqa'
JIRA_PROJECT_KEY = 'MOOG'
JIRA_ISSUE_TYPE = 'Incident' # Default 'Bug'

class jiraClientEscalate(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):

        if alert.status == status:
            return

        if status == 'ack' and alert.attributes['jiraKey'] == "None":
            
            #options = 
            summary = "%s on %s" % (alert.event, alert.resource) 
            description = alert.text
            if 'moreInfo' in alert.attributes:
                description = description + alert.attributes['moreInfo']
            jira_client = JIRA(options={'server': JIRA_API_URL}, basic_auth=(JIRA_API_USERNAME, JIRA_API_PASSWORD))
            issue_dict = {
                'project': {'key': JIRA_PROJECT_KEY},
                'summary': summary,
                'description': description,
                'issuetype': {'name': JIRA_ISSUE_TYPE}
            }
            if 'Insight Id' in alert.attributes:
                issue_dict['customfield_10900'] = alert.attributes['Insight Id']

            if 'Customer' in alert.attributes:
                issue_dict['customfield_10002'] = alert.attributes['Customer']

            if 'jiraProduct' in alert.attributes:
                issue_dict['customfield_10422'] = alert.attributes['jiraProduct']

            try:
                new_issue = jira_client.create_issue(fields=issue_dict)
                alert.attributes['jiraKey'] = str(new_issue)
            except Exception as e:
                raise RuntimeError("Jira: Failed to create issue - %s", e)


        return alert, status, text
