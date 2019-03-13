class User:
    def __init__(self, *,
                 email: str,
                 first_name: str =None,
                 last_name: str =None,
                 full_name: str =None,
                 is_active: bool=True,
                 github_username: str =None,
                 team_name: str =None,
                 slack_id: str =None,
                 employee_type: str =None,
                 manager_fullname: str =None,
                 ) -> None:
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.is_active = is_active
        self.github_username = github_username
        self.team_name = team_name
        self.slack_id = slack_id
        self.employee_type = employee_type
        self.manager_fullname = manager_fullname

    def __repr__(self) -> str:
        return 'User(' \
               'email={!r}, ' \
               'first_name={!r}, ' \
               'last_name={!r},' \
               'full_name={!r},' \
               'is_active={!r},' \
               'github_username={!r},' \
               'team_name={!r},' \
               'slack_id={!r},' \
               'employee_type={!r},' \
               'manager_fullname={!r}' \
               ')'.format(self.email,
                          self.first_name,
                          self.last_name,
                          self.full_name,
                          self.is_active,
                          self.github_username,
                          self.team_name,
                          self.slack_id,
                          self.employee_type,
                          self.manager_fullname)
