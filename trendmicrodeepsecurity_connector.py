#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Python 3 Compatibility imports
from __future__ import print_function, unicode_literals

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Usage of the consts file is recommended
# from trendmicrodeepsecurity_consts import *
import requests
import json
from bs4 import BeautifulSoup


class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class TrendMicroDeepSecurityConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(TrendMicroDeepSecurityConnector, self).__init__()

        self._state = None

        # Variable to hold a base_url in case the app makes REST calls
        # Do note that the app json defines the asset config, so please
        # modify this as you deem fit.
        self._base_url = None

    def _process_empty_response(self, response, action_result):
        self.save_progress("Sem v process empty response")
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR, "Empty response and no information in the header"
            ), None
        )

    def _process_html_response(self, response, action_result):
        self.save_progress("Sem v proces html response")
        # An html response, treat it like an error
        status_code = response.status_code
        if (status_code == 200):
            return RetVal(phantom.APP_SUCCESS, response.text)
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code, error_text)

        message = message.replace(u'{', '{{').replace(u'}', '}}')
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        self.save_progress("Sem v proces json response")
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, "Unable to parse JSON response. Error: {0}".format(str(e))
                ), None
            )

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)
        self.save_progress("Sem pred message error")
        # You should process the error returned in the json
        message = "Error from server. Status Code: {0} Data from server: {1}".format(
            r.__dict__,
            r.text.replace(u'{', '{{').replace(u'}', '}}')
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_text_response(self, r, action_result):
        self.save_progress("Sem v text response")
        if 200 <= r.status_code < 399:
           return RetVal(phantom.APP_SUCCESS, r.text)

        return RetVal(action_result.set_status(phantom.APP_ERROR, r.__dict__), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # Process each 'Content-Type' of response separately
        self.save_progress("Sem v process response")
        # Process a json response
        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)

        if 'text' in r.headers.get('Content-Type', ''):
            return self._process_text_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
            r.__dict__,
            r.text.replace('{', '{{').replace('}', '}}')
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, method="get", data=None, params=None, cookie=None):
        # **kwargs can be any additional parameters that requests.request accepts

        # config = self.get_config()

        resp_json = None
        self.save_progress("Sem pred get attr")
        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, "Invalid method: {0}".format(method)),
                resp_json
            )
        # Create a URL to connect to
        self.save_progress("Sem po get attr")
        url = self._base_url + endpoint
        self.save_progress("PRed request_func")
        try:
            r = request_func(url, json=data, params=params, cookies=cookie)
        except Exception as e:
            self.save_progress("Error")
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, "Error Connecting to server. Details: {0}".format(str(e))
                ), resp_json
            )

        return self._process_response(r, action_result)

    def _make_rest_call_new(self, endpoint, action_result, method="get", data=None, params=None, cookie=None, headers=None):
        # **kwargs can be any additional parameters that requests.request accepts

        # config = self.get_config()

        resp_json = None
        self.save_progress("Sem pred get attr")
        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, "Invalid method: {0}".format(method)),
                resp_json
            )
        # Create a URL to connect to
        self.save_progress("Sem po get attr")
        url = self._nebase_url + endpoint
        self.save_progress("PRed request_func")
        try:
            r = request_func(url, json=data, params=params, cookies=cookie, headers=headers)
        except Exception as e:
            self.save_progress("Error")
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, "Error Connecting to server. Details: {0}".format(str(e))
                ), resp_json
            )

        return self._process_response(r, action_result)

    def _handle_test_connectivity(self, param):
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Connecting to endpoint")
        # make rest call
        self.save_progress("Bla")
        ret_val, response = self._make_rest_call(
            '/apiVersion', action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed.")
            return action_result.get_status()

        # Return success
        self.save_progress("Test Connectivity Passed!")
        self.save_progress(response)
        return action_result.set_status(phantom.APP_SUCCESS, response)

    def _login(self, param, action_result):
        """
        This function logs into DS manager with given credentials and gets the session ID.
        """

        # Filling the payload wth credentials. These are the values that user inputs in Phantom.
        payload = {'dsCredentials': {"tenantName": param['accountname'], "userName": param['username'], "password": param['passwd']}}

        # Making the API call
        ret_val, response = self._make_rest_call(endpoint='/authentication/login', action_result=action_result, method='post', data=payload)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Return sID
        return response

    def _logout(self, param, action_result, sid):
        """
        This function deletes the session.
        """

        # Making the API call.
        ret_val, response = self._make_rest_call(endpoint='/authentication/logout', action_result=action_result, method='delete', params={'sID': sid})

        if phantom.is_fail(ret_val):
           return action_result.get_status()

        return response

    def _handle_get_log_inspection_events(self, param):
        """
        This function returns the max number of events specified in eventsnum.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        c = {"sID": sid}
        # API call to get log inspection events from DS manager
        ret_val, response = self._make_rest_call(endpoint='/events/logInspection', action_result=action_result, method='get', params={'maxItems': param['eventsnum']}, cookie=c)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp)

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_getwebevents(self, param):
        """
        This function returns all web reputation events.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to get all web reputation events from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/events/webreputation', action_result=action_result, method='get', params={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp)

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_list_software_changes(self, param):
        """
        This function list all software changes.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))
        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to list all software changes
        ret_val, response = self._make_rest_call_new(endpoint='/softwarechanges', action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_listcomputers(self, param):
        """
        This function list all computers.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))
        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to list all computers
        ret_val, response = self._make_rest_call_new(endpoint='/computers', action_result=action_result, method='get', headers=headers, params={'expand': 'none'})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_get_comp_fw_rules(self, param):
        """
        This function list all firewall rules of a computer.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers and endpoint
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}
        ep = '/computers/' + str(param['compid']) + '/firewall/rules'

        # API call to get all computer fw rules
        ret_val, response = self._make_rest_call_new(endpoint=ep, action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_describe_computer_setting(self, param):
        """
        This function describes a computer setting.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers and ep
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}
        ep = '/computers/' + str(param['compid']) + '/settings/' + param['setting']

        # API call to lsit computer groups
        ret_val, response = self._make_rest_call_new(endpoint=ep, action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_list_comp_groups(self, param):
        """
        This function lists all computer groups.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to lsit computer groups
        ret_val, response = self._make_rest_call_new(endpoint='/computergroups', action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_list_default_settings(self, param):
        """
        This function lists all default policy settings.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to list policies
        ret_val, response = self._make_rest_call_new(endpoint='/policies/default', action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_list_global_rules(self, param):
        """
        This function list all global rules.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to list policies
        ret_val, response = self._make_rest_call_new(endpoint='/applicationcontrolglobalrules', action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_delete_global_rule(self, param):
        """
        This function deltes the global rule specified by the ruleID.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}
        ep = '/applicationcontrolglobalrules/' + str(param['ruleID'])
        # API call to list policies
        response = requests.delete(self._nebase_url + ep, headers=headers)

        ab = response.status_code
        if ab >= 400:
            return action_result.set_status(phantom.APP_ERROR, ab)

        # Add the response into the data section
        action_result.add_data(response.status_code)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_add_global_rule(self, param):
        """
        This function adds global rule.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing payload
        payload = { "applicationControlGlobalRules": [{"sha256": param['sha256'], "description": param["description"]}]}

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}
        ep = '/applicationcontrolglobalrules'
        # API call to list policies
        ret_val, response = self._make_rest_call_new(endpoint=ep, action_result=action_result, method='post', headers=headers, data=payload)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_listpolicies(self, param):
        """
        This function list all policies
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        # API call to list policies
        ret_val, response = self._make_rest_call_new(endpoint='/policies', action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def _handle_getalerts(self, param):
        """
        This function returns all alerts present on DS manager.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to get all alerts
        ret_val, response = self._make_rest_call(endpoint='/alerts', action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp)

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['alerts'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_getimevents(self, param):
        """
        This function returns all integrity monitoring events from DS manager.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to get all integrity monitoring events
        ret_val, response = self._make_rest_call(endpoint='/events/integrity', action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp)

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['alerts'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_list_report_templates(self, param):
        """
        List all report templates.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)
        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(str(len(param)))

        # Preparing parameters
        payload = {}
        if len(param) != 4:
            for key, value in param.items():
                payload[key] = value
        else:
            payload = None
        self.save_progress(json.dumps(payload))

        # API call to list all report templates
        ret_val, response = self._make_rest_call(endpoint='/reports', action_result=action_result, method='get', params=payload, cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_getwevtime(self, param):
        """
        This function returns all web reputation events after specified time.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        time = param['logt']
        self.save_progress("SSASDASADASDASD" + str(time))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing parameters
        payload = {'eventTime': time, 'eventTimeOp': 'gt', 'sID': sid}

        # API call to get all web reputation events after the specified time from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/events/webreputation', action_result=action_result, method='get', params=payload)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_getevtime(self, param):
        """
        This function returns all antimalware events after specified time.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        time = param['logt']
        self.save_progress("SSASDASADASDASD" + str(time))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # Preparing parameters
        payload = {'eventTime': time, 'eventTimeOp': 'gt', 'sID': sid}

        # API call to get all antimalware events after the specified time from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/events/antimalware', action_result=action_result, method='get', params=payload)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_list_alert_types(self, param):
        """
        This function lists all alert types.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to list all alert types
        ret_val, response = self._make_rest_call(endpoint='/alert-types', action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_list_event_based_tasks(self, param):
        """
        This function lists event based tasks
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to list all event based tasks from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/tasks/event-based', action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_getevents(self, param):
        """
        This function returns all antimalware events.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to get all antimalware events from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/events/antimalware', action_result=action_result, method='get', params={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_describe_alert_type(self, param):
        """
        Describes an alert type.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)

        # API call to describe an alert type from the DS manager
        ret_val, response = self._make_rest_call(endpoint='/alert-types/' + str(param['alertid']), action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_delete_ev_based_task(self, param):
        """
        Delete an event based task.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing link
        ep = self._base_url + '/tasks/event-based/' + str(param['eventid'])

        # API call to delete event based task from the DS manager
        r = requests.delete(ep, cookies={'sID': sid})

        ab = r.status_code
        if ab >= 400:
            return action_result.set_status(phantom.APP_ERROR, ab)

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(ab)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_dismiss_alert_one_target(self, param):
        """
        Dismiss alert on one target.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing endpoint link
        ep = self._base_url + '/alerts/' + str(param['alertid']) + '/target/' + str(param['targetid'])

        # API call to dismiss alert on one target in the DS manager
        r = requests.delete(ep, cookies={'sID': sid})
        ab = r.status_code
        if ab >= 400:
            return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(ab)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_describe_alert(self, param):
        """
        Describes an alert.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # API call to describe an alert on the DS manager
        ret_val, response = self._make_rest_call(endpoint='/alerts/' + str(param['alertid']), action_result=action_result, method='get', cookie={'sID': sid})

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_modify_alert_type(self, param):
        """
        Modifies an alert type.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing modification data
        payload = {"ModifyAlertTypeRequest": {"alertType": {}}}
        self.save_progress(json.dumps(param))
        for key, value in param.items():
            self.save_progress(key)
            if key == 'accountname' or key == 'username' or key == 'passwd' or key == 'context':
                continue
            if key == 'alertid':
                key = 'id'
            payload['ModifyAlertTypeRequest']['alertType'][key] = value
        self.save_progress(json.dumps(payload))

        # API call to modify an alert type on DS manager
        ret_val, response = self._make_rest_call(endpoint='/alert-types/' + str(param['alertid']), action_result=action_result, method='post', cookie={'sID': sid}, data=payload)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_dismiss_alert(self, param):
        """
        Dismiss an alert.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing parameters
        aid = param['alertid']
        self.save_progress(self._base_url + '/alerts/' + str(aid))

        # API call to dismiss an alert
        r = requests.delete(self._base_url + '/alerts/' + str(aid), cookies={'sID': sid})
        ab = r.status_code
        if ab >= 400:
            return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        # action_result.add_data(r.__dict__)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_reset_alert_type(self, param):
        """
        Resets an alert type to default values.
        """
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Calling the login function to get session id
        sid = self._login(param, action_result)

        # If the login function fails
        if phantom.is_fail(sid):
           return action_result.get_status()

        self.save_progress(sid)
        # Preparing parameters
        aid = param['alertid']
        self.save_progress(self._base_url + '/alert-types/' + str(aid))

        # API call to reset alert type
        r = requests.delete(self._base_url + '/alert-types/' + str(aid), cookies={'sID': sid})
        ab = r.status_code
        if ab >= 400:
            return action_result.get_status()

        # Calling the logout function
        resp = self._logout(param, action_result, sid)

        # If the logout function fails
        if phantom.is_fail(resp):
           return action_result.get_status()

        self.save_progress(resp + "NENE")

        # Add the response into the data section
        # action_result.add_data(r.__dict__)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = sid

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, sid)

    def _handle_describe_computer(self, param):
        """
        This function describes a computer.
        """

        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Preparing headers
        headers = {'api-version': self._api_ver, 'api-secret-key': self._auth_token}

        ep = '/computers/' + str(param['compid'])
        # API call to describe a computer
        ret_val, response = self._make_rest_call_new(endpoint=ep, action_result=action_result, method='get', headers=headers)

        # If the call fails
        if phantom.is_fail(ret_val):
           return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({})
        summary['events'] = "Bla"

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS, "Bla")

    def handle_action(self, param):
        # Get the action that we are supposed to execute for this App Run

        self.debug_print("action_id", self.get_action_identifier())

        # Dictionary mapping each action with its corresponding actions
        action_mapping = {
            'test_connectivity': self._handle_test_connectivity,
            'getevents': self._handle_getevents,
            'getwebevents': self._handle_getwebevents,
            'getalerts': self._handle_getalerts,
            'getimevents': self._handle_getimevents,
            'getevtime': self._handle_getevtime,
            'list_alert_types': self._handle_list_alert_types,
            'reset_alert_type': self._handle_reset_alert_type,
            'describe_alert_type': self._handle_describe_alert_type,
            'modify_alert_type': self._handle_modify_alert_type,
            'dismiss_alert': self._handle_dismiss_alert,
            'describe_alert': self._handle_describe_alert,
            'dismiss_alert_one_target': self._handle_dismiss_alert_one_target,
            'list_event_based_tasks': self._handle_list_event_based_tasks,
            'delete_ev_based_task': self._handle_delete_ev_based_task,
            'list_report_templates': self._handle_list_report_templates,
            'listpolicies': self._handle_listpolicies,
            'listcomputers': self._handle_listcomputers,
            'get_comp_fw_rules': self._handle_get_comp_fw_rules,
            'list_comp_groups': self._handle_list_comp_groups,
            'getwevtime': self._handle_getwevtime,
            'describe_computer': self._handle_describe_computer,
            'describe_computer_setting': self._handle_describe_computer_setting,
            'get_log_inspection_events': self._handle_get_log_inspection_events,
            'list_default_settings': self._handle_list_default_settings,
            'list_global_rules': self._handle_list_global_rules,
            'add_global_rule': self._handle_add_global_rule,
            'delete_global_rule': self._handle_delete_global_rule,
            'list_software_changes': self._handle_list_software_changes
        }

        action = self.get_action_identifier()
        action_execution_status = phantom.APP_SUCCESS

        if action in action_mapping.keys():
            action_function = action_mapping[action]
            action_execution_status = action_function(param)

        return action_execution_status

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()
        # Access values in asset config by the name

        # Required values can be accessed directly
        self._base_url = config.get('baseURL')
        self._nebase_url = config.get('baseURLnew')
        self._auth_token = config.get('authtoken')
        self._api_ver = config.get('newAPIversion')

        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


def main():
    import pudb
    import argparse

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = TrendMicroDeepSecurityConnector._get_phantom_base_url() + '/login'

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = TrendMicroDeepSecurityConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json['user_session_token'] = session_id
            connector._set_csrf_info(csrftoken, headers['Referer'])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)


if __name__ == '__main__':
    main()
