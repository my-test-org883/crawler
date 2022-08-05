subprocess_result_side_effect = [
    """... 
... time 1549285022
... 
... path //
... depotFile0 //
... action0 branch
... type0 text+x
... rev0 1
... fileSize0 7013
... digest0 43FF03812C6A49A67D37F3CA6F567202

... 
... time 1553721513
... 
... path //
... old
... depotFile0 //
... action0 edit
... type0 text
... rev0 3
... fileSize0 208366
... digest0 45ADEA5C397C510B31F4851B7F96FF75

...""",
    """... 
... time 1549285022
... 
... path //
... depotFile0 //
... action0 branch
... type0 text+x
... rev0 1
... fileSize0 7013
... digest0 43FF03812C6A49A67D37F3CA6F567202

... 
... time 1553721513
... 
... path //*
... old
... depotFile0 //
... action0 edit
... type0 text
... rev0 3
... fileSize0 208366
... digest0 45ADEA5C397C510B31F4851B7F96FF75

...""",
    "",
    """... 
... time 1553721513
... 
... path //
... old
... depotFile0 //
... action0 edit
... type0 text
... rev0 3
... fileSize0 208366
... digest0 45ADEA5C397C510B31F4851B7F96FF75

...""",
    """... 
... time 1553721513
... 
... path //*
... old
... depotFile0 //
... action0 edit
... type0 text
... rev0 3
... fileSize0 208366
... digest0 45ADEA5C397C510B31F4851B7F96FF75

...""",
    "",
]

subprocess_error_side_effect = [
    """
    "12131214 - no such 
    "Invalid 
    "",
    "19333333 - no such 
    "Invalid 
    "",
    """
]
