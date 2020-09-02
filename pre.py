
import json

data_path = "voa_title_text_best_bert.json"

with open(data_path, "r") as f:
    data = json.load(f)

a = {}
a["data"] = []
aa = {}
aa["title"] = {}

new_exampes = []
for example in data["data"][0]["paragraphs"]:
    paragraphs = example['context'].split("\n")
    all_start = []
    answers = []
    i = 0
    while(1):
        start = 0
        para_start = 0
        if(example['qas'][i]['answers'][0]['answer_start'] not in answers):
            answers.append(example['qas'][i]['answers'][0]['answer_start'])
            for paragraph in paragraphs:
                if(start + len(paragraph) < example['qas'][i]['answers'][0]['answer_start']):
                    start = start + len(paragraph) + 1
                    para_start += 1
                else:
                    break
            all_start.append(para_start)
            i += 1
            if(i == len(example['qas'])):
                break
        else:
            example['qas'].remove(example['qas'][i])
            if(i == len(example['qas'])):
                break
    example['html_text'] = paragraphs
    example['html_start'] = all_start
    new_exampes.append(example)

aa["paragraphs"] = new_exampes
a["data"].append(aa)

with open("voa_title_text_best_bert_html.json", "w") as f:
    json.dump(a, f)
