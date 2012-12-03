from mixcloud.speedbar.db.databasewrapper import wrappedbackend, DatabaseWrapper

# Import everything except DatabaseWrapper from the wrapped backend
locals_dict = locals()
for k in wrappedbackend.__dict__:
    if not k.startswith('__') and not k.endswith('__') and k != 'DatabaseWrapper':
        locals_dict[k] = wrappedbackend.__dict__[k]

