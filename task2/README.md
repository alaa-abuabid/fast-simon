**Task2 - Google App Engine Database App**
This is a simple database app deployed on Google App Engine. The app supports a set of commands to manage variables, 
including setting, getting, unsetting, and querying variables. It also includes an Audit feature for tracking variable 
changes over time.

**application url**: https://task2-dot-charged-state-451616-h7.ew.r.appspot.com

**Features**
SET: Set the value of a variable.
GET: Retrieve the value of a variable.
UNSET: Remove a variable.
NUMEQUALTO: Count how many variables have a specific value.
UNDO: Undo the most recent SET or UNSET command.
REDO: Redo the most recent undone SET or UNSET command. 
END: Clean up all stored variables in the datastore.
AUDIT: Track the history of changes made to a specific variable.

**Note on REDO Command Behavior:**
The official documentation states that if more than one consecutive REDO command is issued, the original commands should be redone in the original order of execution. Additionally, it specifies that if another command (such as GET or NUMEQUALTO) is executed after an UNDO, the REDO command should do nothing.
However, after testing with the provided sequences, I found that the REDO command should still work even if GET or 
NUMEQUALTO commands were issued after an UNDO. This is the behavior implemented in the app.

**Endpoints**
https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/set: Set a variable's value.
GET /set?name={variable_name}&value={variable_value}

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/get: Get the value of a variable.
GET /get?name={variable_name}

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/unset: Unset a variable.
GET /unset?name={variable_name}

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/numequalto: Count how many variables are set to a given value.
GET /numequalto?value={variable_value}

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/undo: Undo the most recent SET or UNSET command.
GET /undo

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/redo: Redo the most recent undone SET or UNSET command.
GET /redo

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/end: Clean up all data in the datastore.
GET /end

https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/audit: Get the history of a variable.
GET /audit?name={variable_name}

**Proposed Feature: Variable History (Audit)**
This feature allows you to track the history of a variable. The Audit endpoint returns a list of all past values and 
their timestamps for a given variable.

Endpoint: Audit
URL: https://task2-dot-charged-state-451616-h7.ew.r.appspot.com/audit?name={name}
Description: Returns the history of changes (timestamp and value) for the specified variable {name}.

Example:
Request: /audit?name=variable1

Response:

variable variable1 audit
1. 2025-02-22 10:30 | 10
2. 2025-02-22 10:40 | 20

How the Audit Feature Improves the App
The Audit feature enhances the app by providing a transparent history of variable changes, including timestamps, which 
improves data traceability. It helps users track when and what values were set, aiding in error resolution and debugging.
This feature ensures data integrity and adds a layer of accountability, making the app more reliable.


