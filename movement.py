# This function has two inputs, one includes 'accx', 'accy', 'accz', 'gyrox', 'gyroy','gyroz' and 'speed', another one is the pretrained model
# This function has one output, which is the movement ID, 0: straight, 1: U-turn. 2: Right turn
# Please be careful for the structure of input 'X', it shoule be a 2D array with shape (1,7)
# For example:
# [[accx  accy  accx  gyrox
#   gyroy gyroz speed]]
def movement_classifier(X, model_path):
    
    from joblib import load

    model = load(model_path)

    pred = model.predict(X)

    return pred