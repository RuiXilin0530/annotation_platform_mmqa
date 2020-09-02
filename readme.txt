Developed on April 2020.

有可能只选择了一侧的数据。

data format
{
    'pid'
    'title': [[cat1], tt1, [cat2], tt2],
    "medical": {
        'url'
        'head'
        'contents': [[stid, eng_sent, chn_sent], ...]
        }
    'health': 同上
}

label result
{
    'pid'
    'label_results': [
        {
            ...,
            'result': [
                {'medical':[...], 'health':[...], 'e_sent': 'xxx', 'ne_sent': 'xxx'},
                ...
                ]
        }
    ]
}