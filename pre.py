
import json

data_path = "voa_title_text_best_bert_html.json"

with open(data_path, "r") as f:
    data = json.load(f)


with open("voa_caption_events.cs", "r") as f:
    a = f.readlines()
all_entity = {}
a = a[2:]
for aa in a:
    aaa = aa.split("\t")
    if(len(aaa) == 5):
        entity_id = aaa[0].strip(":")
        aaa[2] = aaa[2].strip("\"")
        if(entity_id not in all_entity):
            b = []
            b.append(aaa[2])
            all_entity[entity_id] = b
        elif(aaa[2] not in all_entity[entity_id]):
            all_entity[entity_id].append(aaa[2])

a = {}
a["data"] = []
aa = {}
aa["title"] = {}

num = 0

new_exampes = []
for example in data["data"][0]["paragraphs"][0:6000]:
    context = example['context']
    all_start = []
    answers = []
    i = 0
    while(1):
        ans_start = example['qas'][i]['answers'][0]['answer_start']
        flag = 0
        for key in all_entity:
            for value in all_entity[key]:
                if(value == example['qas'][i]['answers'][0]['text']):
                    flag = 1
                    break
            if(flag):
                example['qas'][i]['answers'][0]['ans_all'] = all_entity[key]
                break
        if(example['qas'][i]['answers'][0]['text'] not in context):
            print(context[ans_start: ans_start + len(example['qas'][i]['answers'][0]['text']) + 10])
            print(example['qas'][i]['answers'][0]['text'])
            flag = 0
            for value in example['qas'][i]['answers'][0]['ans_all']:
                if(value in context):
                    flag = 1
                    break
            if(flag == 0):
                print(example['qas'][i]['answers'][0]['ans_all'])
        i += 1
        if(i == len(example['qas']) or flag == 0):
            break
                
                        

    #     start = 0
    #     para_start = 0
    #     if(example['qas'][i]['answers'][0]['answer_start'] not in answers):
    #         answers.append(example['qas'][i]['answers'][0]['answer_start'])
    #         for paragraph in paragraphs:
    #             if(start + len(paragraph) < example['qas'][i]['answers'][0]['answer_start']):
    #                 start = start + len(paragraph) + 1
    #                 para_start += 1
    #             else:
    #                 break
    #         all_start.append(para_start)
    #         i += 1
    #         if(i == len(example['qas'])):
    #             break
    #     else:
    #         example['qas'].remove(example['qas'][i])
    #         if(i == len(example['qas'])):
    #             break
    # example['html_text'] = paragraphs
    # example['html_start'] = all_start
    if(flag):
        example['id'] = num
        num += 1
        new_exampes.append(example)
print(len(new_exampes))
aa["paragraphs"] = new_exampes
a["data"].append(aa)

with open("voa_title_text_best_bert_html_sample.json", "w") as f:
    json.dump(a, f)

