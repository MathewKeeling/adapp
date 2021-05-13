'''
# COMPLETE: input user return membership of distribution groups
# COMPLETE: Return List of Orphaned Users:

Changes made to include some security groups that were not included. See entries in OU=USERS,DC=DOMAIN,DC=COM
Changes made to better represent groups w/ empty
Moved OU/CN indicator to the OU/CN execution code block. Stopped repeated entries of OU/CN when an OU/CN did not include
    apropriate contents.

2.5 separated get groupmembers method from get members method.
    List generated expanded from ~1900 lines to ~6500 lines. The change accounts for the nested groups.
    Code is now fully recursive. Every nested group is expanded.

need to sort the master list of groups.

2.6 disabled infinite recursion. Need to make it a flag that you can tick to enable or disable.
    Reduced ~6500 lines to ~4500 lines

GOAL: Specify a Distribution list and report back a tree of every group and subsidiary nested group and users.
'''
from ldap3 import Connection, Server, BASE, LEVEL, Connection, SUBTREE, ALL, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES


def dntocn(dn):  # convert a DistinguishedName to a CanonicalName
    dn = str(dn)
    dn = dn[3:dn.index(',')]
    return dn


def comparelist(raw, members):
    userlist = raw
    tempmembers = []
    for key in members:
        tempmembers.append(key)
    orphanedusers = set(userlist).difference(set(tempmembers))
    return orphanedusers


def getgroups(groupdict, tabs=0, distgroupsfqdns = 'dc=domain,dc=com'):
    global groupsList
    conn.search(
        search_base='{}'.format(distgroupsfqdns),
        search_filter='(| '
                      '(objectClass = Group)'
                      '(objectCategory = CN=Group,CN=Schema,CN=Configuration,DC=domain,DC=com)'
                      '(sAMAccountType = 268435457)'
                      '(objectClass=OrganizationalUnit)'
                      '(objectCategory=Container))',
        search_scope=LEVEL,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    for member in conn.entries:
        dn = str(member.distinguishedName)
        if ('sAmaccountType' in member):  # If entry is a group
            groupsList['{}'.format(str(member.cn))] = '{}'.format(str(member.distinguishedName))  # ['Common Name']:['FQDN']
        else:  # if entry is a Container or an Organization Unit
            getgroups(groupdict, tabs + 1, member.distinguishedName)
    return(groupsList)


def getmembers(tabs=0, distgroupsfqdns = 'dc=domain,dc=com'):
    prettyprintstr = ''  # local variable that stores # of tabs to print.
    for i in range(0, tabs):
        prettyprintstr = prettyprintstr + '\t'
    prettyprintstr = prettyprintstr + '\t'  # Tab Out Subsidiary Users & Groups
    conn.search(
        search_base='{}'.format(distgroupsfqdns),
        search_filter='(| '
                      '(objectClass = Group)'
                      '(objectCategory = CN=Group,CN=Schema,CN=Configuration,DC=domain,DC=com)'
                      '(sAMAccountType = 268435457)'
                      '(objectClass=OrganizationalUnit)'
                      '(objectCategory=Container))',
        search_scope=LEVEL,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    for member in conn.entries:
        dn = str(member.distinguishedName)
        if 'sAmaccountType' in member:  # If entry is a group
            getmembersofgroup(member.distinguishedName, tabs)
        else:  # if member is a Container or an Organization Unit
            print(prettyprintstr + 'OU/CN:' + str(dntocn(distgroupsfqdns)), ' ', member.distinguishedName)  # Print the OU/CN
            getmembers(tabs + 1, member.distinguishedName)


def getmembersofgroup(distgroupfqdns, tabs):
    global memberdict
    prettyprintstr = ''
    for i in range(0, tabs):
        prettyprintstr = prettyprintstr + '\t'
    conn.search(
        search_base='{}'.format(distgroupfqdns),
        search_filter='(objectClass=group)',
        search_scope=SUBTREE,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
    )
    for member in conn.entries:
        if 'member' in member:  # if the group has members
            print(prettyprintstr + '\tGroup: {}'.format(dntocn(member.distinguishedName)))  # Print Group
            for x in range(0, len(member.member)):
                if dntocn(member.member[x]) in groupsList:
                    getmembersofgroup(member.member[x], tabs=tabs+1)
                else:
                    memberdict.append(dntocn(member.member[x]))  # add user to list of nonorphanedusers
                    print(prettyprintstr + '\t\tUser: {}'.format(dntocn(member.member[x])))  # Print user.
        elif 'member' not in member:  # if the group does not have members
            print(prettyprintstr + '\tGroup: ', dntocn(member.distinguishedName))
            print(prettyprintstr + '\t\tEMPTY')


def getusers(searchbase):  # get a master list of users (without disabled users)
    global userList
    conn.search(
        search_base='{}'.format(searchbase),  # Select domain of search
        search_filter='(& '
                      '(objectclass=person)'
                      '(mail=*@*.*)'
                      '(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))',
        search_scope=SUBTREE,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]  # select attributes to pull in search
    )
    for e in conn.entries:
        userList = userList + [str(e.cn)]
    return(userList)


# Variable Declaration Block
userList = []
memberdict = []
members2 = []
groupsList = {}
# Program code
print('|----------------------------------------------------|')
print('|    ~~~ ACTIVE DIRECTORY DOMAIN MEMBER TOOL ~~~     |')
print('|   This is the ADDMT. The domain is domain.com    |')
print('|----------------------------------------------------|\n')
#user_name = input('Please enter your AD User Name: ')
user_name = 'userNameHere'
#password = input('Please enter your AD password: ')
password = 'passwordHere'
server = Server('ldap://domain.com:389', get_info=ALL)  # port 389 is the default non secure port. 636 is ssl/tls
conn = Connection(server, 'domain\\' + user_name, password, auto_bind=True)
users = getusers('dc=domain,dc=com')
print('|--------------------------------------------------------------------|')
print('| This is the list of distribution groups and members on the domain: |')
print('|--------------------------------------------------------------------|')
groupsList = getgroups(groupsList)
getmembers()
orphanedUsers = sorted(list(comparelist(users, memberdict)))
print('\n|--------------------------------------------------------------------|')
print('| This is the list of groups:                                        |')
print('|--------------------------------------------------------------------|')
for key, value in groupsList.items():
    print('\t', 'Group: ', key)  # , ' : ', 'FQDN: ', value)
print('\n|--------------------------------------------------------------------|')
print('| This is the list of orphaned users:                                |')
print('|--------------------------------------------------------------------|')
for entry in orphanedUsers:
     print('\tUser: {}'.format(entry))