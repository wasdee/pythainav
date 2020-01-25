# PythaiNAV
*ทำให้การดึงข้อมูล* ***กองทุนไทย*** *เป็นเรื่องง่าย*


## Get Started - เริ่มต้นใช้งาน

ติดตั้ง PythaiNAV ก่อน
```bash
pip install pythainav
```

```python
>>> import pythainav as nav

>>> nav.get("KT-PRECIOUS")
Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS')

>>> nav.get("TISTECH-A")
Nav(value=12.9976, updated='21/01/2020', tags={'latest'}, fund='TISTECH-A')

```
