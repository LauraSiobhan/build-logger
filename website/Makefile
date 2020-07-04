REMOTE_HOST = obairlann.net
REMOTE_DIR = .html/aviation/biplane/buildlog

all: deploy

deploy: deploy_index deploy_dashboard deploy_data deploy_statdata deploy_table

deploy_index: index.html
	scp index.html $(REMOTE_HOST):$(REMOTE_DIR)

deploy_dashboard: dashboard-total.js dashboard.js
	scp dashboard.js dashboard-total.js $(REMOTE_HOST):$(REMOTE_DIR)

deploy_data: data.py
	scp data.py $(REMOTE_HOST):$(REMOTE_DIR)

deploy_statdata: statdata.py
	scp statdata.py $(REMOTE_HOST):$(REMOTE_DIR)

deploy_table: table.js
	scp table.js $(REMOTE_HOST):$(REMOTE_DIR)

