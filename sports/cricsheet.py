"""Cricsheet JSON match parser. Aggregates match event data; keeps source attribution visible."""
import json
from collections import defaultdict
from zipfile import ZipFile, BadZipFile

def _add_match(info, innings):
    date=(info.get('dates') or ['Unknown'])[0]
    teams=info.get('teams') or []
    comp=(info.get('competition') or {}).get('name','Cricket') if isinstance(info.get('competition'),dict) else str(info.get('competition') or 'Cricket')
    venue=info.get('venue','Unknown venue')
    stats=defaultdict(lambda:{'runs':0,'balls_faced':0,'fours':0,'sixes':0,'wickets':0,'runs_conceded':0,'balls_bowled':0,'matches':1,'teams':set()})
    for team in teams:
        for s in stats.values(): s['teams'].add(team)
    for inn in innings or []:
        for over in inn.get('overs',[]):
            for delivery in over.get('deliveries',[]):
                batter=delivery.get('batter'); bowler=delivery.get('bowler')
                runs=delivery.get('runs') or {}; batter_runs=int(runs.get('batter',0)); total=int(runs.get('total',0)); extras=delivery.get('extras') or {}
                if batter:
                    stats[batter]['runs']+=batter_runs
                    if 'wides' not in extras: stats[batter]['balls_faced']+=1
                    if batter_runs==4: stats[batter]['fours']+=1
                    if batter_runs==6: stats[batter]['sixes']+=1
                if bowler:
                    stats[bowler]['runs_conceded']+=total-int(extras.get('byes',0))-int(extras.get('legbyes',0))-int(extras.get('penalty',0))
                    if 'wides' not in extras and 'noballs' not in extras: stats[bowler]['balls_bowled']+=1
                    for wicket in delivery.get('wickets',[]):
                        kind=wicket.get('kind')
                        if kind not in {'run out','retired hurt','obstructing the field'}: stats[bowler]['wickets']+=1
    return [{'player':name,'match_date':date,'competition':comp,'venue':venue,'teams':' vs '.join(teams),'runs':s['runs'],'balls_faced':s['balls_faced'],'fours':s['fours'],'sixes':s['sixes'],'wickets':s['wickets'],'runs_conceded':s['runs_conceded'],'balls_bowled':s['balls_bowled']} for name,s in stats.items()]

def parse_json_bytes(data):
    obj=json.loads(data.decode('utf-8-sig'))
    if not isinstance(obj,dict) or 'info' not in obj or 'innings' not in obj: raise ValueError('JSON is not a Cricsheet match file (expected info and innings fields).')
    return _add_match(obj['info'],obj['innings'])

def parse_upload(filename,data):
    rows=[]
    if filename.lower().endswith('.json'):
        rows=parse_json_bytes(data)
        for row in rows: row['match_id']=filename.rsplit('/',1)[-1].rsplit('\\',1)[-1].rsplit('.',1)[0]
        return rows
    if not filename.lower().endswith('.zip'): raise ValueError('Upload a Cricsheet JSON file or JSON ZIP archive.')
    try:
        with ZipFile(__import__('io').BytesIO(data)) as archive:
            json_files=[n for n in archive.namelist() if n.lower().endswith('.json') and not n.startswith('__MACOSX/')]
            if not json_files: raise ValueError('This ZIP has no JSON match files.')
            for name in json_files:
                try:
                    match_rows=parse_json_bytes(archive.read(name))
                    for row in match_rows: row['match_id']=name.rsplit('/',1)[-1].rsplit('\\',1)[-1].rsplit('.',1)[0]
                    rows.extend(match_rows)
                except (ValueError,KeyError,TypeError): continue
    except BadZipFile as e: raise ValueError('The uploaded ZIP file is invalid.') from e
    if not rows: raise ValueError('No valid Cricsheet JSON match files were found in this archive.')
    return rows
