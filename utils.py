import cv2
from functools import reduce

cat_list = [
    'shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 
    'pants', 'shorts', 'skirt', 
    'coat', 'dress', 'jumpsuit', 'cape', 
    'hat', 'headband, head covering, hair accessory', 
    'leg warmer', 'tights, stockings', 'shoe'
    ]

categories = {
    'head': ['hat', 'headband, head covering, hair accessory'],
    'body': ['shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 'dress', 'jumpsuit', 'cape'],
    'pants': ['pants', 'shorts', 'skirt'],
    'boots': ['leg warmer', 'tights, stockings', 'shoe']
}

def correct_clothing_bounding_boxes(human_bbox, clothes):
    # Extract the coordinates of the human bounding box
    hxmin, hymin, hxmax, hymax = human_bbox

    # Check if dress is detected
    if clothes['body']['label'] in ['dress', 'jumpsuit', 'cape']:
        # Readjust so that it touches the entire human border
        clothes['body']['box']['xmin'] = hxmin
        clothes['body']['box']['xmax'] = hxmax
        
        # Spare the rest of the space for foot and head
        clothes['boots']['box'] = {'xmin': hxmin, 'ymin': clothes['body']['box']['ymax'], 'xmax': hxmax, 'ymax': hymax}

        if clothes['head'] is None:
            clothes['head'] = {}

        clothes['head']['box'] = {'xmin': hxmin, 'ymin': hymin, 'xmax': hxmax, 'ymax': clothes['body']['box']['ymin']}

    else:
        clothes['body']['box']['xmin'] = hxmin
        clothes['body']['box']['xmax'] = hxmax

        # Spare the rest of the space for the head and feet
        clothes['boots']['box'] = {'xmin': hxmin, 'ymin': clothes['pants']['box']['ymax'], 'xmax': hxmax, 'ymax': hymax}
        if clothes['head'] is None:
            clothes['head'] = {}

        clothes['head']['box'] = {'xmin': hxmin, 'ymin': hymin, 'xmax': hxmax, 'ymax': clothes['body']['box']['ymin']}

    return clothes

# Helper function to compute intersection over union (IoU)
def iou(box1, box2):
    
    # Calculate the coordinates of the intersection box
    xmin_inter = max(box1['xmin'], box2['xmin'])
    ymin_inter = max(box1['ymin'], box2['ymin'])
    xmax_inter = min(box1['xmax'], box2['xmax'])
    ymax_inter = min(box1['ymax'], box2['ymax'])
    
    # Calculate the area of the intersection box
    intersection_area = max(0, xmax_inter - xmin_inter) * max(0, ymax_inter - ymin_inter)
    
    # Calculate the area of both bounding boxes
    box1_area = (box1['xmax'] - box1['xmin']) * (box1['ymax'] - box1['ymin'])
    box2_area = (box2['xmax'] - box2['xmin']) * (box2['ymax'] - box2['ymin'])
    
    # Calculate the area of the union
    union_area = box1_area + box2_area - intersection_area
    
    # Calculate IoU
    iou_value = intersection_area / union_area if union_area != 0 else 0

    return iou_value
    
def calculate_area(pred):
    return (pred['xmax'] - pred['xmin']) * (pred['ymax'] - pred['ymin'])
    
def subset_categories(preds, cat):
    return [pred for pred in preds if pred['label'] in cat]

def finalize_predictions(preds, threshold=0.7):
    selected = {'head': None, 'body': None, 'pants': None, 'boots': None}
    for key in categories.keys():
        try:
            subset = subset_categories(preds, categories[key])
            selected[key] = subset[0]

        except Exception as e:
            print(f"Encountered error {e}, continuing...")
    
    if selected['pants'] is not None and selected['body'] is not None:
        overlap_iou = iou(selected['body']['box'], selected['pants']['box'])
        print(overlap_iou)
        selected['pants'] = None if overlap_iou > 0.5 else selected['pants']

    return selected
    