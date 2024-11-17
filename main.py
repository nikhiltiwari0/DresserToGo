from utils import *
from stitch import *
from pipeline import *
# Load model directly
from transformers import AutoImageProcessor, AutoModel
import torch

def service_model(filename):
    image = cv2.imread(filename, cv2.IMREAD_COLOR)

    # Load the model and preprocessor
    pipe = HumanClothesDetectionPipeline()
    
    # Generate the predictions
    human, preds = pipe(filename)

    # Sort the predictions by area size
    preds.sort(key=lambda x: calculate_area(x['box']), reverse=True)

    # Generate for each category and select the highest
    final_predictions = finalize_predictions(preds)

    # Correct the proportions of the detections
    corrected_predictions = correct_clothing_bounding_boxes(human.values(), final_predictions)

    # Save the cropped images
    meta_data_list = []
    for i, key in enumerate(corrected_predictions.keys()):
        # Skip looping if there are no detection
        if corrected_predictions[key] is None:
            pass

        else:
            try:
                for bound in corrected_predictions[key]['box'].keys():
                    corrected_predictions[key]['box'][bound] = int(corrected_predictions[key]['box'][bound])

                xmin, ymin, xmax, ymax = corrected_predictions[key]['box'].values()

                # Save the image using OpenCV
                cropped_image = image[ymin:ymax, xmin:xmax, :]
                cv2.imwrite(filename[:-4]  + f"_{i}" + ".jpg", cropped_image)

                # Save the metadata
                meta_data_list.append({
                    'isLiked': False,
                    'clothingType': corrected_predictions[key]['label'],
                    'length': ymax - ymin,
                    'width': xmax - xmin
                })

            except Exception as e:
                print(f'Encountered error {e} while cropping, continuing...')

    return meta_data_list

def create_stitched_images(files):
    stitched_image = stitch_images(files)
    stitched_image = replace_black_with_majority_color(stitched_image)
    cv2.imwrite('stitched.png', stitched_image)

class SimiliaritySearcher:
    def __init__(self, model_dir="abhishek/autotrain_fashion_mnist_vit_base"):
        self.processor = AutoImageProcessor.from_pretrained(model_dir)
        self.model = AutoModel.from_pretrained(model_dir)

    def extract_embeddings(self, image):
        with torch.no_grad():
            embeddings = self.model(**image).last_hidden_state[:, 0].detach()

        return embeddings
    
    def compute_similarity(self, emb1, emb2):
        scores = torch.nn.functional.cosine_similarity(emb1, emb2)
        return scores.numpy().tolist()