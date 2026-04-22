


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # ✅ Force evaluation immediately
    branches = list(Branch.objects.all())
    self.fields['branch'].queryset = branches

    self.fields['department'].queryset = []

    if 'branch' in self.data:
        try:
            branch_id = int(self.data.get('branch'))
            departments = list(Department.objects.filter(branch_id=branch_id))
            self.fields['department'].queryset = departments
        except (ValueError, TypeError):
            pass