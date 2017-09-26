import os
import jinja2

def report_inline_user():
    pass

def createreport(userlist):

    cwd = os.getcwd()
    templatedir = cwd +  "/templates"
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    maintemplate = templateEnv.get_template(templatedir + "/main.jinja")
    keytemplate = templateEnv.get_template(templatedir + "/key.jinja")
    tabletemplate  = templateEnv.get_template(templatedir + "/table.jinja")
    inlineusertemplate = templateEnv.get_template(templatedir + "/inlineuser.jinja")
    nonmfausaaerstemplate = templateEnv.get_template(templatedir + "/mfauser.jinja")

    keytablecontent = ""
    for auser in userlist:
        for key in auser.return_api_access_keys_json():
            templateVars = {"key": json.loads(key)}
            keytablecontent += keytemplate.render(templateVars)

    keyheadings = ["Name", "Creation", "ID", "Unused", "LastUsedTooLong", "KeyTooOld"]

    keytabletemplateVars = {"headings": keyheadings,
                    "tablecontents": keytablecontent,
                    "id": "keys",
                        }

    keytablecontent = tabletemplate.render(keytabletemplateVars)

    #table for inline policy users
    inlineusers = ""
    for auser in userlist:
        if auser.inline_enabled:
            inlinetemplatevars  = {"name": auser.username,
                "inline_policy_list": auser.inline_policy_list,
                "image": auser.avatar,
                "administrative": auser.administrative
                }

            inlineusers += inlineusertemplate.render(inlinetemplatevars)

    nonmfausers = ""
    for auser in userlist:
        if not auser.service_account:
            inlinetemplatevars  = {"name": auser.username,
                "image": auser.avatar,
                "administrative": auser.administrative
                }
            nonmfausers += nonmfausaaerstemplate.render(inlinetemplatevars)


    maintemplateVars = {"title": "Fluffy Output",
                    "description": "Hopefully simple output",
                    "keytablecontents": keytablecontent,
                    "inlineusers": inlineusers,
                    "nonmfausers": nonmfausers,
                    }

    with open("Output/index.html", "wb") as fh:
        fh.write(maintemplate.render(maintemplateVars))

        known_aws_admin_policies = get_list_from_config_parser(config.get('aws', 'known_aws_admin_policies'))
        known_aws_admin_groups = get_list_from_config_parser(config.get('aws', 'known_aws_admin_groups'))

        userlist = []


        createreport(userlist)