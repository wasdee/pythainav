import factory
import itertools

class_type = ["A", "D", "R"]
class_type_name = ["ชนิดสะสมมูลค่า", "ชนิดจ่ายเงินปันผล", "ชนิดขายคืนหน่วยลงทุนอัตโนมัติ"]


def get_class_name(o):
    return class_type_name[class_type.index(o.class_abbr_name)]


class SearchClassFundFactory(factory.Factory):
    class Meta:
        model = dict

    proj_id = factory.Sequence(lambda n: "M{:0>4}_25{:0>2}".format(n, n))
    last_upd_date = "2020-01-01T01:02:03"
    proj_abbr_name = factory.Sequence(lambda n: "FUND-{:0>2}".format(n))
    class_abbr_name = factory.Iterator(itertools.cycle(class_type))
    class_name = factory.LazyAttribute(get_class_name)
    class_additional_desc = factory.Faker("text")
