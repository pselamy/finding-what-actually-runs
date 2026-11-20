import re

import desk
import team


path = re.compile(r"/api/drafts/[a-z0-9-]+")


def handlers_for(workspace):
    selected = {"personal": desk.save, "shared": team.save}[workspace]
    return ((path, selected),)
