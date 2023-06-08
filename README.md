# conventional-precommit-linter

### Tests
```sh
pytest
```
or ... create a content in file `test_message.txt` and run:
```sh
python -m conventional_precommit_linter.hook --subject-min-length 20 --subject-max-length 50 --body-max-line-length 100 test_message.txt
```

or (with default arguments):
```sh
python -m conventional_precommit_linter.hook test_message.txt
```



### Credit
Inspired by project: https://github.com/compilerla/conventional-pre-commit
