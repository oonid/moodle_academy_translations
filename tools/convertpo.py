# created by oon@oo.or.id
# using library polib: `pip install polib`

from argparse import ArgumentParser
from csv import DictReader, DictWriter
from pathlib import Path
from sys import exit
from json import dumps, loads
from polib import POFile, POEntry, pofile

parser = ArgumentParser()
parser.add_argument("src")
parser.add_argument("dst")
parser.add_argument("-p", "--to_po", action="store_true")
parser.add_argument("-c", "--to_csv", action="store_true")

args = parser.parse_args()

print(f'src: {args.src}')
print(f'dst: {args.dst}')

if args.src == args.dst:
    print(f'src must not equal to dst.')
    exit()

target_src = Path(args.src)
target_dst = Path(args.dst)

if not target_src.is_file() and not target_src.exists():
    print(f'{args.src} not exists.')
    exit()

if target_dst.is_file() and target_dst.exists():
    print(f'{args.dst} already exists, will be overwritten.')

headers_upload = ['md5key', 'rawtext', 'substitutetext', 'targetlanguage', 'contextid']
# translation-toolkit headers_weblate = ['location', 'source', 'target', 'ID', 'fuzzy', 'context', 'translator_comments', 'developer_comments']

if args.to_po:
    _to_po = True  # from csv to po
elif args.to_csv:
    _to_po = False  # from po to csv
else:
    print('define --to_po or --to_csv')
    exit()

if _to_po:  # from import/export csv file to po format

    with open(target_src) as csv_src:
        reader_src = DictReader(csv_src)
        _headers = reader_src.fieldnames
        if _headers != headers_upload:
            print('--to-po needs predefined CSV with headers: {headers_upload}')
            exit()

        po = POFile()
        po.metadata = {
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

        for row in reader_src:
 
            json_comment = {
                'targetlanguage': row['targetlanguage'],
                'contextid': row['contextid'],
                'md5key': row['md5key'],
            }
            entry = POEntry(
                msgid=row['rawtext'],
                msgstr=row['substitutetext'],
            #    occurrences=[(row['contextid'], ''), (row['md5key'], '')],
                tcomment=dumps(json_comment)
            )
            po.append(entry)

        po.save(target_dst)

else:  # from po format to import/export csv file

    with open(target_dst, 'w') as csv_dst:
        writer_dst = DictWriter(csv_dst, fieldnames=headers_upload)
        writer_dst.writeheader()
 
        po = pofile(target_src)
        for entry in po:
            json_comment = loads(entry.tcomment)
            row = {}
            for k in headers_upload:
                if k == 'rawtext':
                    row[k] = entry.msgid
                elif k == 'substitutetext':
                    row[k] = entry.msgstr
                else:
                    row[k] = json_comment[k]
            writer_dst.writerow(row)

