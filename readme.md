<!-- this is a readme file -->
# Active Directory Distribution Membership Tool (ADDMT)
Version 2.7 | M. Keeling | 05/11/2021
<!-- space for new entry-->
#### Requisite Libraries:
- ldap3
---
## Project Goals
### Checklist
- [X] Create a Search LDAP Syntax Friendly Search Function (5/27)
- [X] Create a Search Function That Lists all Active Directory User Accounts (5/26)
- [X] Create a Search Function That Lists All Active Directory Distribution Groups
- [X] Create a Search Function That Lists all Active Directory Distribution Lists
- [X] Create a Function that creates (a) list(s) of members for each Distribution Group.
- [X] Create a Function that creates (a) list(s) of members for each Distribution List.
- [X] Convert LDAP User Function into Method
- [X] Convert LDAP Distribution Group Function to Method **5/29 @ 5:10 PM**
- [X] Convert LDAP Distribution List Function to Method
- [X] Convert Distribution Group (list) Function to Method
- [X] Convert Distribution List (list) Function to Method
- [X] Convert Method for Audit to Recursive method **5/29 @ 5:10 PM**
- [X] Store Audit to memory
- [ ] Export Audit to CSV (or similar)
- [ ] GOAL: Input a user a name, return Member of for user (**LDAP**)
- [ ] *LDAPSearchExclusionGroup* (Make a group whose role is to exclude non applicable orphans through membership) (**LDAP**)
- [ ] input a user name OR A GROUP, and return a list of EVERY directory they have privileges to access (**NTFS, ACL, FileExplorer**)
- [ ] GOAL: ACL integration (**NTFS, ACL, FileExplorer**)

<!-- space for new entry-->

---
## Helpful resources:
[Recursion Video](https://www.youtube.com/watch?v=mz6tAJMVmfM) <br />
[LDAP3 Library Documentation](https://ldap3.readthedocs.io/en/latest/searches.html?highlight=search) <br />
[LDAP SearchFilters (Distribution)](https://ldapwiki.com/wiki/Active%20Directory%20Group%20Related%20Searches) <br />
[LDAP SearchFilters (All)](https://ldapwiki.com/wiki/LDAP%20SearchFilters) <br />
[ADUAC Attributes](https://docs.secureauth.com/display/KBA/Active+Directory+Attributes+List) <br />
[Python Object Types](https://www.tutorialspoint.com/python/python_tuples.htm) <br />
<!-- space for new entry-->

---
## Changelog
<!-- space for new entry-->

---
#### ADDMT - 2.7<br />
05/11/2021
- Removed some Information.
- Reconfigured repo.
<!-- space for new entry-->

---
#### ADDMT - 2.5<br />
6/4/2020
- Fully Searches Entire Active directory
- Returns Every User that is not a member of a group
<!-- space for new entry-->

---
#### ADDMT - 2.0<br />
6/2/2020
- This version is the console version.
- This version successfully generates a list of all distribution groups on the domain.
- This version successfully generates a list of all orphaned users on the domain.

NEW GOALS:
- GOAL: Input a user a name, return Member of for user LDAP
- input a user name OR A GROUP, and return a list of EVERY directory they have privileges to access in a hierachical FE
- GOAL: What is an ACL? Find out what folders they have access and denies. FE
- \<LDAPSearchExclusionGroup\> (Make a group whose role is to exclude non applicable orphans through membership)
<!-- space for new entry-->

---
#### ADDMT - 1.35 <br />
##### 'adappRecursiveHybrid.py' is the latest working prototype.
- Added Function to convert CN (Canonical Name) to DN (Distinguished Name)
- Added Function to generate whole list of users on the domain
- Modified getmembers function to spit out all users the same way, regardless of whether or not they are inside of a group, a container, or an organizational unit.
- NEED TO IMPLEMENT A DATA STORAGE METHOD. CONSIDER WHAT PRINTING FUNCTIONS WILL LOOK LIKE FOR CSV-LIKE APPLICATIONS.
<!-- space for new entry-->

---
#### ADDMT - 1.3 <br />
- Third Experimental Release
```python
'''
Rewrite.
This version searches for a dynamic base, and sequentially evaluates.
Need to work out storage class. (Or Dictionary)
Version exists that just prints. See: adappRecursiveTestActualPrint.py
'''

- Recursive Method Code:
```python
'''
### This Method prints results. It does not store it to a useable working memory.
def getmembers(memberdict, tabs=0, distgroupsefqdns = 'dc=domain,dc=com'):
    prettyprintstr = ''
    for i in range(0, tabs):
        prettyprintstr = prettyprintstr + '\t'
    print(prettyprintstr+'group: '+str(distgroupsefqdns))

    conn.search(
        search_base='{}'.format(distgroupsefqdns),
        search_filter='(| (sAMAccountType = 268435457)'
                      '(sAmaccountType = 805306368)'
                      '(objectClass=OrganizationalUnit)'
                      '(objectCategory=Container))',
        search_scope=LEVEL,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    prettyprintstr = prettyprintstr + '\t'
    for member in conn.entries:
        dn = str(member.distinguishedName)
        if ('sAmaccountType' in member) and (member['sAmaccountType'] == 805306368):
            print(prettyprintstr+'user: '+str(member.cn))
            if dn in memberdict:
                print('dupe! {}'.format(dn))
                memberdict[dn] = memberdict[dn] + 1
            else:
                memberdict[dn] = 1
        elif ('sAmaccountType' in member) and (member['sAmaccountType'] == 268435457):
            if ('member' in member):
                print(prettyprintstr + 'members: {}'.format(member.member))
        else:
            getmembers(memberdict, tabs + 1, member.distinguishedName)
'''
```
<!-- space for new entry-->

---
#### ADDMT - 1.2 (XI) <br />
- SECOND EXPERIMENTAL RECURSIVE release
```python
'''
# This version works, but something is wrong.
# Groups with subsidiary groups, their members do not appear.
# I don't know if it is because recursion is not working... Or if it is because on the second time around the data is just being written to a new dictionary key with name 'groupC' and then when it is 'groupC''s turn to be recorded, it just overrites the subsidiary 'groupC's key.
# I don't know how to test...
'''
```
##### RECURSION CODE:
```python
def GetMembers(distgroupfqdn):
    global memberList, rawMemberList
    memberList = []
    rawMemberList = []
    conn.search(
        search_base='dc=domain,dc=com',
        search_filter='(memberOf={})'.format(distgroupfqdn),
        search_scope=SUBTREE,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    for member in conn.entries:
        try:
            if member.sAMAccountType == 268435457:  # a group's objectCategory = 'CN=Group,CN=Schema,CN=Configuration,DC=domain,DC=com'
                # memberList = memberList + list('Members of {} group: '.format(str(member.cn)))
                GetMembers(escape_filter_chars(str(member.distinguishedName)))
            elif member.sAMAccountType == 805306368:
                memberList = memberList + list(member.cn)
                memberList = sorted(memberList)
        except LDAPCursorError:
            desc = ' '
```
<!-- space for new entry-->

---
#### ADDMT - 1.1 <br />
- FIRST EXPERIMENTAL RECURSIVE release
- All Recursive Code is on recursiveTestActual.py
```python
def GetMembers(distgroupfqdn):
    conn.search(
        search_base='dc=domain,dc=com',
        search_filter='(memberOf={})'.format(distgroupfqdn),
        search_scope=SUBTREE,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    for member in conn.entries:
        if member.sAMAccountType == 268435457: # a group's objectCategory = 'CN=Group,CN=Schema,CN=Configuration,DC=domain,DC=com'
            print('This is a group: ', member.cn)
            GetMembers(escape_filter_chars(str(member.distinguishedName)))
        elif member.sAMAccountType == 805306368:
            print('This is a user: ', member.cn)
```
<!-- space for new entry-->

---
#### ADDMT - 1.0 <br />
- First functional release.
- Still using iterative methods.
- NEED RECUSION! NEED RECURSION! NEED RECURSION!

Features the following functions:
```python
print('|----------------------------------------------------------------------------------------------------------|')
print('|1. Generate a complete list of users on the domain.                                                       |')
print('|2. Generate a list of distribution groups and lists on the domain.                                        |')
print('|3. Generate an Audit of all Groups and all Users of those Groups. Account for orphaned users.|')
print('|----------------------------------------------------------------------------------------------------------|')
```
<!-- space for new entry-->

---
#### ADDMT - 0.9 <br />
5/28/2020 1:15 PM
- 0.9
- Can generically search whole AD for all groups and return a list for all members of all groups.
- HOWEVER: It is not recursive, and it CANNOT list the groups within groups.
- I am still trying out how to store the data properly
```python
exampleList = {'dnlocation' : 'member1', 'member2', 'member3'}
#  It needs to be able to be searched by 'dnlocation', and the members should be able to be added to.
```
<!-- space for new entry-->

---
#### ADDMT - 0.85<br />
5/27/2020 8:52 PM
- Used to be called 0.8
- Successfully completed one iteration of the goal.
- Need recursion to solve the rest of problem.
- See video:
[Recursion Video](https://www.youtube.com/watch?v=mz6tAJMVmfM)
<!-- space for new entry-->

---
#### ADDMT - 0.8<br />
5/27/2020 4:10 PM
- Successful list generation for a given distribution group.
- NEED to figure out a way to generate a X.500 compliant FQDN for a given distribution group.
<!-- space for new entry-->

---
#### ADDMT - 0.7<br />
5/27/2020
Useful Documentation on LDAP3 <br />
[LDAP3 Library Documentation](https://ldap3.readthedocs.io/en/latest/searches.html?highlight=search)

- Added useful comments about functions of LDAP3 search() method.
- Better familiarized w/ how the method returns results. Currently working out how to get them to funnel into a manipulable variable format. (What type would be best.)

```python
# [variable -> . -> ( < search_base [FQDN] > , < ldap filter syntax > , < attributes to be searched >
conn.search('dc=domain,dc=com', '(&(objectclass=person)(mail=*@*.*)(givenName=*))', attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
```

<!-- space for new entry-->

---
#### ADDMT - 0.6<br />
5/26/2020
- First search function works. It only populates a list of every active user account with an email account.
  ```python
  conn.search('dc=domain,dc=com', '(&(objectclass=person)(mail=*@*.*)(givenName=*))', attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
  ```

---
#### ADDMT - 0.5<br />
5/26/2020
- Implemented Search function
- Search is broken. It only returns last created user. Needs work.
- Need more understanding on how search works...
<!-- space for new entry-->

---
#### ADDMT - 0.4<br />
5/26/2020
- Implemented better arrangement in markdown.
- Changed scheme for recording lists to unordered lists (from numbered lists)
- Changed naming scheme
- Realized the reason code blocks weren't working was because you have to use carrots and not apostrophes.
- Revised all prior change logs.
- Moved changelog chronologically
<!-- space for new entry-->

---
#### ADDMT - 0.3<br />
5/26/2020
- Further tested the commit function.
- You have to commit before you run push
```shell
  $ git commit -m 'Information about change here'
  $ git push origin master
```
<!-- space for new entry-->

---
#### ADDMT - 0.2<br />
5/26/2020

- Tested pushing data to git.
<!-- space for new entry-->

---
#### ADDMT - 0.1<br />
5/26/2020
- Created Project Folder
- Created readme.md in the project folder
- Created git account.
<!-- space for new entry-->

---
