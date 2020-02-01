# PythaiNAV: ทำให้การดึงข้อมูลกองทุนไทยเป็นเรื่องง่าย
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![Github_workflow_tatus](https://img.shields.io/github/workflow/status/CircleOnCircles/pythainav/Python%20package)](https://github.com/CircleOnCircles/pythainav/actions?query=workflow%3ATests)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/CircleOnCircles/pythainav.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/CircleOnCircles/pythainav/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/CircleOnCircles/pythainav.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/CircleOnCircles/pythainav/alerts/)



![cover image](https://github.com/CircleOnCircles/pythainav/raw/master/extra/pythainav.png)



> อยากชวนทุกคนมาร่วมพัฒนา ติชม แนะนำ เพื่อให้ทุกคนเข้าถึงข้อมูลการง่ายขึ้น [เริ่มต้นได้ที่นี้](https://github.com/CircleOnCircles/pythainav/issues) หรือเข้ามา Chat ใน [Discord](https://discord.gg/jjuMcKZ) ได้เลย 😊

📖 Documentation is here. คู่มือการใช้งานอยู่ที่นี่ <https://pythainav.nutchanon.org/>

## Get Started - เริ่มต้นใช้งาน

```bash
$ pip install pythainav
```

```python
import pythainav as nav

nav.get("KT-PRECIOUS")
> Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS')

nav.get("TISTECH-A")
> Nav(value=12.9976, updated='21/01/2020', tags={'latest'}, fund='TISTECH-A')

```

## Source of Data - ที่มาข้อมูล

ตอนนี้ใช้ข้อมูลจาก website <https://www.finnomena.com/fund>

## Disclaimer

เราไม่ได้เกี่ยวข้องกับ "finnomena.com" แต่อย่างใด เราไม่รับประกันความเสียหายใดๆทั้งสิ้นที่เกิดจาก แหล่งข้อมูล, library, source code,sample code, documentation, library dependencies และอื่นๆ

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://nutchanon.org"><img src="https://avatars2.githubusercontent.com/u/8089231?v=4" width="100px;" alt=""/><br /><sub><b>Nutchanon Ninyawee</b></sub></a><br /><a href="https://github.com/CircleOnCircles/pythainav/commits?author=CircleOnCircles" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!