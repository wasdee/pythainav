# Data Sources - แหล่งข้อมูล

PythaiNAV สามารถดึงข้อมูลได้จากแหล่งข้อมูล 3 แหล่ง

| แหล่งข้อมูล                                                                                                     | parameter name | require key            | อ้างอิง API                                                            | หมายเหตุ                                        |
| --------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------- | ---------------------------------------------------------------------- | ----------------------------------------------- |
| <https://www.finnomena.com/fund>                                                                                | `"finnomena"`  | -                      | [Postman](https://www.getpostman.com/collections/b5263e2bf12b42d87061) |                                                 |
| <https://api-portal.sec.or.th/>                                                                                 | `"sec"`        | `subscription_key`     | [Postman](https://www.getpostman.com/collections/7283814ab1851c58b68a) | กำลังพัฒนา                                      |
| [http://dataexchange.onde.go.th/](http://dataexchange.onde.go.th/DataSet/3C154331-4622-406E-94FB-443199D35523#) | `"onde"`       | `subscription_key`\*\* | [Postman](https://www.getpostman.com/collections/acc26820945b2c6776fd) | ไม่สามารถสมัครเพื่อขอรับ `subscription_key` ได้ [*ref*](http://dataexchange.onde.go.th/DataSet/92b67f7e-023e-4ce8-b4ba-08989d44ff78) |
