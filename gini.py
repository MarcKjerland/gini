def gini(data,target,ranking=None,weight=None,plot=True,ascending=True):
    """ Plot Lorenz curve and return Gini coefficient
        Useful to measure income inequality (in an economics context)
        or to evaluate a risk model's rank ordering (in an insurance context).
    
    Parameters
    ----------
    data : Pandas DataFrame or H2OFrame
        Input data containing observed and predicted values
    target : string
        Column name of target variable, representing income (economics) or incurred loss (insurance)
    ranking : string (default=None)
        Column name of variable that ranks target, i.e. predicted expected loss (insurance).
        If left blank this will be identical to the target variable.
    weight : string (default=None)
        Column name of optional weight variable, i.e. earned exposure (insurance)
        If left blank all records will have equal weight.
    plot : Boolean
        Determines whether to plot Lorenz curve using matplotlib.
        If the input is an H2OFrame, it will be converted to Pandas DataFrame.
        Default is True.
    ascending : Boolean
        Determines whether the Lorenz curve should be under the diagonal or over.
        If the input is True, it will be under the diagonal.
        Default is True.

    Returns
    -------
    gini_coefficient : Between 0 and 1

    Examples
    --------
    >>> g = gini(my_data,'income',plot=False)
    >>> g
    0.18
    
    >>> g = gini(my_data,'actual_loss','predicted_loss',weight='earned_car_years',plot=False)
    >>> g
    0.16
    
    >>> g = gini(my_data,'actual_loss','predicted_loss',plot=False)
    >>> g
    0.14
    
    """

    if ranking is None:
        ranking = target
    
    if "pandas" in str(type(data)):
        
        # Sort records by predicted value
        if weight is None:
            sorted_data = data.sort_values(by=ranking,ascending=ascending)[[target]]
            weight = "weight"
            sorted_data[weight] = 1
        else:
            sorted_data = data.sort_values(by=ranking,ascending=ascending)[[target,weight]]
        sorted_data = sorted_data.reset_index(drop=True)
    
    elif "H2OFrame" in str(type(data)):
    
        # Sort records by predicted value
        if weight is None:
            sorted_data = data.sort(by=ranking,ascending=ascending)[[target]]
            weight = "weight"
            sorted_data[weight] = 1
        else:
            sorted_data = data.sort(by=ranking,ascending=ascending)[[target,weight]]
    
    else:
        print("Error: Invalid data type " + str(type(data)) + " . Expected Pandas DataFrame or H2OFrame.")
        return -1

    # Rescale so sums are 1
    sorted_data[target] = sorted_data[target] / sorted_data[target].sum()
    sorted_data[weight] = sorted_data[weight] / sorted_data[weight].sum()

    # Compute running totals
    sorted_data["cumul_total"] = sorted_data[target].cumsum()
    sorted_data["cumul_weight"] = sorted_data[weight].cumsum()

    # Compute Gini coefficient
    # equal to twice the area between the Lorenz curve and the diagonal
    sorted_data["lift"] = ( sorted_data["cumul_weight"] - sorted_data["cumul_total"] ) * sorted_data[weight] 
    if ascending == True:
        gini_index = 2 * sorted_data["lift"].sum()
    else:
        gini_index = -2 * sorted_data["lift"].sum()

    # Plot Lorenz curve
    if plot == True:
        import matplotlib.pyplot as plt
        # Subsample data to reduce plotting overhead
        n = sorted_data.shape[0]
        if n > 1000:
            stride = int(n/1000)
        else:
            stride = 1
        if "pandas" in str(type(data)):
            data_subsample = sorted_data[["cumul_total","cumul_weight"]].iloc[::stride]
        else: # H2OFrame
            data_subsample = sorted_data[::stride,["cumul_total","cumul_weight"]].as_data_frame()
            
        plt.plot(data_subsample["cumul_weight"],data_subsample[["cumul_total","cumul_weight"]])
        plt.show()
    
    return gini_index


