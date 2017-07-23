def distance(dt):
    # dt: the sampling time must be greater than
    # alist,vlist,dlist must be initilized if classes not imported
    total_distance = 0
    alist.append(imu.get_point())
    if len(alist) == 3 :
        vlist.append(imu.tpaz(alist[0],alist[1],0.03))
    if len(vlist) == 3:
        dlist.append(imu.tpaz(vlist[0],vlist[1],0.03))
    if len(dlist) == 3:
        total_distance = total_distance + dlist[0]
