# PythaiNAV
*ทำให้การดึงข้อมูล* ***กองทุนไทย*** *เป็นเรื่องง่าย*


## Get Started - เริ่มต้นใช้งาน

ติดตั้ง PythaiNAV ก่อน
```bash
pip install pythainav
```

```python
import pythainav as nav

nav.get("KT-PRECIOUS")
> Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS')

nav.get("TISTECH-A", date="1 week ago")
> Nav(value=12.9976, updated='14/01/2020', tags={}, fund='TISTECH-A')

nav.get_all("TISTECH-A", range="MAX")
> [Nav(value=12.9976, updated='21/01/2020', tags={}, fund='TISTECH-A'), Nav(value=12.9002, updated='20/01/2020', tags={}, fund='TISTECH-A'), ...]

nav.get_all("KT-PRECIOUS", asDataFrame=True)
> pd.DataFrame [2121 rows x 4 columns]
```
