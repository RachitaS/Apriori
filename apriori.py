import csv
from collections import defaultdict
from itertools import combinations

def nextBiggerGroupsWhithin(groups):
    prefixAndfreq = defaultdict(list)
    groups = groups.keys()
    l = len(groups[0])
    for group in groups:
        prefixGroup = ''.join(sorted(group)[:l - 1])
        prefixAndfreq[prefixGroup].append(group)
    nextGroups = []
    for prefixGroup, freq in prefixAndfreq.items():
        if len(freq) > 1:
            for c in combinations(freq, 2):
                nextGroups.append(c[0].union(c[1]))
        else:
            del prefixAndfreq[prefixGroup]
    return nextGroups
def getTransactionData(file_name):
    try:
        with open(file_name) as f:
            content = f.readlines()
            f.close()
    except:
        print 'Error in opening input file'
        return
    Txns = []
    for line in content:
        Txns.append(frozenset(line.strip().split(',')))
    return Txns
def printOutputToFile(outputFile, rules,itemListOfDict,Txns,flag):
    f = open(outputFile,'w')
    l=0
    final_items=[]
    for groups in itemListOfDict:
        if len(groups) == 0:
            continue
        formatted_groups = []
        for group,dummy in groups.iteritems():
            formatted_groups.append((','.join(sorted(map(str, group)))))
       
	l = l + len(formatted_groups)
        for group in formatted_groups:
	    final_items.append(group)
    f.write(str(l))
    f.write('\n')
    for item in final_items:
    	f.write(item)
    	f.write('\n')

    if(flag=='1'):
        formatted_rules = [(','.join(sorted(map(str, r[0]))) + ' => ' + ','.join(sorted(map(str, r[1])))) for r,dummy in rules]
    	f.write(str(len(formatted_rules)))
    	f.write('\n')
        for fr in formatted_rules:
	    f.write(fr)
	    f.write('\n')
    f.close()

def main():
    global Txns
    global confidence
    global support

    conf=[]
    try:
        with open('config.csv', 'r') as csvfile:
       	    lines = csv.reader(csvfile)
	    conf = list(lines)	
    except:
        print 'Error in opening config file '
        return

    for l in conf:
    	c = l[0]
	o=l[1]
    	if(c=='input'):
		input_file=o
	elif(c=='output'):
		output_file=o
	elif(c=='support'):
		support=float(o)
	elif(c=='confidence'):
		confidence=float(o)
	else:
		flag=o

    Txns = getTransactionData(input_file)
    itemListOfDict = [defaultdict(int)]

# FREQUENT ITEMSETS
    # single items
    for Txn in Txns:
        for item in Txn:
            itemListOfDict[0][frozenset([item])] = itemListOfDict[0][frozenset([item])]+1
   
    for key,val in itemListOfDict[0].items():
        if float(val) / len(Txns) < support:
            del itemListOfDict[0][key]

    # groups of multiple items incrementing one by one
    try:
        nextGroups = nextBiggerGroupsWhithin(itemListOfDict[0])
    except IndexError:
    	print "Index ERROR"
        return
    while(len(nextGroups) != 0):
        itemListOfDict.append(defaultdict(int))
        for item_set in nextGroups:
            for Txn in Txns:
                if item_set.issubset(Txn):
                    itemListOfDict[-1][item_set] = itemListOfDict[-1][item_set]+1
	for key,val in itemListOfDict[-1].items():
	    if float(val) / len(Txns) < support:
	        del itemListOfDict[-1][key]
        try:
            nextGroups = nextBiggerGroupsWhithin(itemListOfDict[-1])
        except IndexError:
            break

#ASSOCIATION RULES

    associationRules = []
    # Because we need not consider groups of size 1 as it will not participate in any association rule.
    L = list(itemListOfDict)[1:]
    for groups in L:
	    finalRules = []
	    for group, freq in groups.iteritems():
		
		finalRightss = []
		oneRightRules = []
		for c in combinations(group, 1):
			right = frozenset(c)
			left = group - right
			leftLen = itemListOfDict[len(left) - 1]
			conf = float(freq) / leftLen[left]
			if conf >= confidence:
				finalRightss.append(right)
				oneRightRules.append(((left, right), conf))
		
		finalRules.extend(oneRightRules)
		if len(group)>2:
		    tmpRules = []
		    rlen = 2
		    while(len(finalRightss) != 0 and
			  rlen < len(group)):
			tmpRights = []
			for c in combinations(finalRightss, 2):
			    right = c[0].union(c[1])
			    if len(right) != rlen:
				continue
			    left = group - right
			    leftLen = itemListOfDict[len(left) - 1]
			    conf = float(freq) / leftLen[left]
			    if conf >= confidence:
				tmpRights.append(right)
				tmpRules.append(((left, right), conf))
			finalRightss = tmpRights
			rlen = rlen + 1
		    finalRules.extend(tmpRules)
	    associationRules.extend(list(set(finalRules)))

    printOutputToFile('output.csv',associationRules,itemListOfDict, Txns,flag)

Txns=[]
confidence=0
support=0
main()
