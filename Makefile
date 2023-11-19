FLASK_HOST=0.0.0.0
FLASK_APP=ri_flask

flask_test: $(FLASK_APP).py
	@flask --app $(FLASK_APP) run --debug --host $(FLASK_HOST)


actions:
	@printf "flask_test\tRun Flask Test\n"
	@printf "actions\t\tThis menu\n"
