**To run test use 


generic:
```
cd test
pytest -k "not dcc"
python -m unittest discover -p "test_*" -k "not dcc"
```
maya:

```
// usd mayapy.exe from "C:\Program Files\Autodesk\Maya<version>\bin\mayapy.exe"
mayapy -m unittest discover test/maya -p "dcc_test_*.py"
```