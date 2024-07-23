import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
from django.core.files.base import ContentFile
from django.core.files import File



'''
Image Pre-Processing:
First, the image gets rescaled to 10 pixels per mm. We then rotate the image to make the feet point up.
We then filter the contours of the feet through filter_contours, so that we can create masks.
Per feet we create two masks, one that only contains the footprint itself (inner_image of the contours)
and one that contains everything outside of the footprint (outer_image).
Prior to detecting points, we apply crop_and_mirror, which crops the image given the contour, so that
we end up with either the left foot or the right foot, seperately.

Point Detection:
In process_foot, we call two functions for the created masks respectively.
First, we call the function points_of_interest, which is the function
responsible for detecting points. In points_of_interest we apply adaptive thresholding,
which is there to make the points easier to detect when applying the blob detection.
For the blob detection, we specified the parameters through the settings. Some of the
settings are adjusted prior to calling points_of_interest to adapt to the given mask.
At the end of the points_of_interest function, we create new PointOfInterest objects,
which do not get assigned a role at that point.

Role Assignment:
After detecting the points, the roles get assigned. For this, there are two different
functions, depending on the mask it is applied on. 
The function assign_roles_inside first creates three rectangles in total. From top to bottom, the first rectangle captures
the points describing the toes, the next rectangle describes the six points positioned
after the toes and the last rectangle is responsible for the last four points within the
footprint. We then iterate through all found points and check, in which rectangle a point
falls in. At the end, we have three lists, high, low and mid, which capture the points in
their respective rectangle.
As the first two boxes are relatively close to each other, we check if the distance from the
highest keypoint to the lowest keypoint in the middle rectangle has an appropriate length (midDiff).
If it is too long, it could be, that a point from the upper rectangle was included in the 
mid rectangle. If that is the case, we adjust the boxes, until the middle rectangle does not contain any
point of the upper rectangle. lower_rect_height is set low by design, so that we first always run into
the case that the middle rectangle contains points from the upper rectangle.
With the three lists, we sort the first two by the x-Axis, ascending for the right foot and descending for
the left foot (value of reverse). For the last rectangle, we sort the points by the y-Axis, descending.
In assign_roles_outside, we apply an approach similar to assign_roles_inside, but now we have four rectangles,
the highest one for the point with role 0, the lowest one for the one with role 20, and the ones inbetween
for 6,7 and 18,19, respectively. For the rectangles inbetween, we additionally check, if the point detected
in one of the two rectangles in the middle falls to the left, or to the right for correct role assignment.
'''

# In[37]:


class PointOfInterest:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role

    def __str__(self):
        return "(%s, %s) %s" % (self.x, self.y, self.role)


class FootScannerResult:
    def __init__(self, image, contour, pointsOfInterest):
        self.image = image
        self.contour = contour
        self.pointsOfInterest = pointsOfInterest
        

    def draw(self, contours=True, pointsOfInterest=True):
        image = self.image.copy()
        # Return an image with contours and points of interest drawn if specified
        if contours:
            cv2.drawContours(image, self.contour, -1, (0, 0, 0), 20)
        if pointsOfInterest:
            # Draw detected blobs as red circles
            # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
            keypoints = [cv2.KeyPoint(x=poi.x, y=poi.y, size=40) for poi in self.pointsOfInterest]
            image = cv2.drawKeypoints(image, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return image


class FootScanner:
    def __init__(self, settings):
        self.settings = settings
        self.errors = []

    def get_scaling_points(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh, image_thresh= cv2.threshold(image_gray,55,255,cv2.THRESH_BINARY_INV)#30-35
        #Find the three points
        params = cv2.SimpleBlobDetector_Params()
    
        params.filterByColor = True
        params.blobColor = 0

        # Filter by Area.
        params.filterByArea = True
        params.minArea = 850
        
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity =0.4

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.4

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.4

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs (array contains all points)
        keypoints = detector.detect(image_thresh)


        image_thresh = cv2.drawKeypoints(image_thresh, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        
        return keypoints

    def closest_number(self, lst, target):
        return min(lst, key=lambda x: abs(x - target))
    
    def middle_number(self, lst):
        sorted_numbers = sorted(lst)
        return sorted_numbers[1]
    
    def rescale_image_by_factor(self, image, scaling_factor):
        resized_image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation = cv2.INTER_CUBIC)
        return resized_image

    def get_scaling_factor_from_marker(self, image, desired_mmtopx):
        UPPER_ARM_LENGTH = 100 # 100 mm -> 10cm
        UNDER_ARM_LENGTH = 50
        #image = cv2.imread(imagePath)
        keypoints = self.get_scaling_points(image) 
        # Calculate the lengths of the sides in pixels

        assert len(keypoints) == 3
        # Calculate the lengths of all sides in pixels
        side_lengths = []
        for i in range(3):
            for j in range(i+1,3):
                side_length = np.linalg.norm(np.array(keypoints[i].pt) - np.array(keypoints[j].pt))
                side_lengths.append(side_length)
        
        
        pixel_length = self.middle_number(side_lengths)  # Second longest side
        
        current_scale = pixel_length/UPPER_ARM_LENGTH #how many pixels per real-life millimeter
        

        # Get scaling factor to rescale image to e.g., 10pixels per mm if desired_mmtopx=10
        scaling_factor = desired_mmtopx/current_scale 
        return scaling_factor

    def rescale_image(self, image,desired_mmtopx):
        scaling_factor = self.get_scaling_factor_from_marker(image, desired_mmtopx)

        # Resize the image
        resized_image = self.rescale_image_by_factor(image, scaling_factor)
        
        return resized_image

    #Crop image as to specified border reduction
    #Scanning also works without cropping image
    def _crop_image(self, image, border_size=1):
        image_cropped = image[border_size:-border_size, border_size:-border_size]
        return image_cropped
    

    #Filter out contours that do not belong to a foot    
    def _filter_contours(self,image):     
        #original_image = cv2.imread(imagePath)
        #Now the cropping should begin
        #take the image and turn it gray
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

        #remove the black points to only show the contour
        _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((15, 15), np.uint8) 
        
        binary_image_er = cv2.erode(binary_image, kernel,iterations=2)
        binary_image_er = cv2.dilate(binary_image_er, kernel,iterations=2)
        binary_image_er = cv2.erode(binary_image, kernel)
        
        #crop the images
        binary_image_er_cropped = self._crop_image(binary_image_er)
        gray_image_cropped = self._crop_image(gray_image)
        
        # Find contours in the binary image
        contours, _ = cv2.findContours(binary_image_er_cropped, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        rgb_image = cv2.cvtColor(gray_image_cropped, cv2.COLOR_GRAY2RGB)

        # Create a copy of the original image to draw the contours
        contour_image = rgb_image.copy()

        # Draw contours on the image
        cv2.drawContours(contour_image, contours, -1, (255, 0, 0), 20)

        filtered_contours = []
        # find contours that have a certain aspect ratio -> 

        # Specify the target aspect ratio (change this value accordingly)
        target_aspect_ratio = .4

        # Create a copy of the original image to draw the filtered contours
        filtered_contours_image = gray_image_cropped.copy()

        # Filter contours based on aspect ratio
        filtered_contours = []

        min_contour_area = 500000  # minimum contour area to keep
        #max_contour_area = 5000  # maximum contour area to keep
        for contour in contours:
            # Calculate the bounding box of the contour
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            

            # Calculate the aspect ratio
            aspect_ratio = w / h if h != 0 else 0

            # Define a tolerance for aspect ratio matching
            aspect_ratio_tolerance = 0.2

            # Check if the aspect ratio is close to the target
           
            if abs(aspect_ratio - target_aspect_ratio) < aspect_ratio_tolerance and min_contour_area < area:
                filtered_contours.append(contour)
                cv2.drawContours(filtered_contours_image, [contour], -1, (0, 255, 0), 20)
            
            # Sort the contours from left to right
            filtered_contours = sorted(filtered_contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
        
        return filtered_contours
    
    #Detect the keypoints on the image
    def _points_of_interest(self,image,settings):
        #image = cv2.fastNlMeansDenoisingColored(image)
        
        gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        # Apply denoising
        #gray_image=cv2.fastNlMeansDenoising(gray_image,None, h=self.settings.h, templateWindowSize=self.settings.templateWindowSize, searchWindowSize=self.settings.searchWindowSize) #25 intensity
        #thresh, image_thresholded = cv2.threshold(image, self.settings.maxThreshold, 255, cv2.THRESH_BINARY)
        
        image_thresholded = cv2.adaptiveThreshold(gray_image, 255, 
                                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 
                                                  settings['blocksize'], settings['C'])
        bgr_threshold = np.array(settings['bgr_threshold']) 

        mask = np.all(image > bgr_threshold, axis=2) 

        image_thresholded[mask] = 255  
        
       
        #plt.imshow(image_thresholded)
        #plt.show()
        
        params = cv2.SimpleBlobDetector_Params()

        # Filter by Area.
        params.filterByArea = True
        params.minArea = settings['area']
       
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = settings['circularity']

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = settings['convexity']

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = settings['inertia']

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs (array contains all points)
        keypoints = detector.detect(image_thresholded)

        #Image with keypoints drawn used to edit
        image_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # Create new points of interest, roles assigned later
        points_of_interest = []
        for keypoint in keypoints:
            point_of_interest = PointOfInterest(keypoint.pt[0],keypoint.pt[1],...)
            points_of_interest.append(point_of_interest)
        return points_of_interest

    def _crop_and_mirror(self,image, contour, margin=50):
        # Calculate the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)
        image = image.copy()

        # Expand the bounding box to include a 50px margin
        x -= margin
        y -= margin
        w += 2 * margin
        h += 2 * margin

        mirrored = False

        # Check if the expanded bounding box exceeds image dimensions
        if x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
            mirrored = True
            # Mirror the image within the expanded bounding box
            mirrored_image = cv2.copyMakeBorder(image, margin, margin, margin, margin, cv2.BORDER_REFLECT)
            
            mirrored_x = int((margin/2)) + x 
            mirrored_y = int((margin/2)) + y
            mirrored_w = w + (2 * margin)
            mirrored_h = h + ( 2* margin)
            cropped_image = mirrored_image[mirrored_y:mirrored_y + mirrored_h, mirrored_x:mirrored_x + mirrored_w]
            # Adjust contour coordinates for cropping and mirroring
            adjusted_contour = contour - (mirrored_x - margin, mirrored_y - margin)
        else:
            # Crop the image within the expanded bounding box
            cropped_image = image[y:y + h, x:x + w]
            # Adjust contour coordinates for cropping
            adjusted_contour = contour - (x,y)

        return cropped_image, adjusted_contour, mirrored
    
    # Check if the point falls within the given rectangle
    def is_point_in_rect(self, point, rect):
        x1, y1, x2, y2 = rect
        return x1 <= point.x <= x2 and min(y1, y2) <= point.y <= max(y1, y2)
    

    def find_role_index(self, points_of_interest, role):
        for index, point in enumerate(points_of_interest):
            if point.role==role:
                return index
        print(f"Point with role {role} not found")
        return None
    

    def create_outer_boxes(self,highest_point,lowest_point,rect_w,upper_mid_height,padding,upper_box_extension):
            under =  0, highest_point[0][1], rect_w, highest_point[0][1]-padding
            mid_under =  0, highest_point[0][1], rect_w, highest_point[0][1]+upper_mid_height
            mid_upper =   0, highest_point[0][1]+upper_mid_height, rect_w, lowest_point[0][1]-upper_box_extension
            upper =  0, lowest_point[0][1]-upper_box_extension, rect_w, lowest_point[0][1]+padding
            
            return under, mid_under, mid_upper, upper
    



 # Assign roles of points based on their region
    def sort_and_select_roles_outside(self,keypoints,under,mid_under,mid_upper,upper,rect_w,reverse):
        upper_box = []
        for point in keypoints:
            if self.is_point_in_rect(point, upper):
                upper_box.append(point)
            elif self.is_point_in_rect(point, under):
                point.role = 20
            elif self.is_point_in_rect(point, mid_upper):
                if reverse:
                    point.role = 7 if point.x  < rect_w//2 else 6
                else:
                    point.role = 6 if point.x  < rect_w//2 else 7
            elif self.is_point_in_rect(point, mid_under):
                if reverse:
                    point.role = 18 if point.x < rect_w//2 else 19
                else:
                    point.role = 19 if point.x < rect_w//2 else 18
            else:
                print('Check the boxes.')
                point.role = -1

        if len(upper_box) == 2:
            upper_box[0].role = 0
            upper_box[1].role = 21
        elif len(upper_box)== 1:
            upper_box[0].role = 0
        return keypoints
    
    def assign_roles_outside(self, outer_image, contour, keypoints,reverse):    

        image = outer_image.copy()

        #highest point -> bottom of the heel
        highest_point = min(contour, key=lambda coord: coord[0][1])
        #lowest point -> top of the big toe
        lowest_point = max(contour, key=lambda coord: coord[0][1])

        rect_w = image.shape[1]  #width of boxes, as rectangles begin at 0, take width of image
        padding = self.settings.get_setting('outside')['padding']  #height of highest and lowest box, important: should be padding value
        upper_mid_height = 1100 #value to adjust
        upper_box_extension = 150 # extend upper box to the bottom to incorporate points with roles 0 and 21

        
        under, mid_under, mid_upper, upper = self.create_outer_boxes(highest_point,lowest_point,rect_w,upper_mid_height,padding,upper_box_extension)
        keypoints = self.sort_and_select_roles_outside(keypoints,under,mid_under,mid_upper,upper,rect_w,reverse)

        # create cutpoints for keypoint pairs
        for i in [(self.find_role_index(keypoints,21),self.find_role_index(keypoints,20)), #creating the cutpoints for 21 first leads to the cutpoint of 20 being already set
                  (self.find_role_index(keypoints,0),self.find_role_index(keypoints,20)), #thus cutpoint 20 does not change here
                  (self.find_role_index(keypoints,6),self.find_role_index(keypoints,7)),
                  (self.find_role_index(keypoints,18),self.find_role_index(keypoints,19))
                  ]:
            if i[0] is not None and i[1] is not None:
                keypoints[i[0]], keypoints[i[1]] = self.find_cutpoints(contour, keypoints[i[0]], keypoints[i[1]])
        
        return keypoints
    

    def create_inner_boxes(self,highest_point,lowest_point,upper_rect_height,mid_rect_height, rect_width):
            rect_low = (0, highest_point[0][1], rect_width, upper_rect_height)
            rect_mid = (0, upper_rect_height, rect_width, upper_rect_height + mid_rect_height)
            rect_high = (0, upper_rect_height + mid_rect_height, rect_width, lowest_point[0][1])

            return rect_low, rect_mid, rect_high
    
    def assign_inner_points_to_boxes(self,pointsOfInterest,rect_low,rect_mid,rect_high):
            high = []
            mid = []
            low = []

            #For all found points, check where the points 
            for point in pointsOfInterest:
                if self.is_point_in_rect(point, rect_high):
                    high.append(point)
                elif self.is_point_in_rect(point, rect_low):
                    low.append(point)
                elif self.is_point_in_rect(point, rect_mid):
                    mid.append(point)
            return high,mid,low
    

    def sort_and_select_roles_inside(self,batches,reverse):

            sorted_inner_points =[]
            expected_lengths = [5, 6, 4]

            high = batches[0]
            mid = batches[1]

            # Sort every batch here to give them the correct role
            for index, batch in enumerate(batches):
                # If we sort the high/mid points, we sort by x-Axis from left to right
                if index == 0 or index == 1:#batch is high or mid:
                    sorted_batch = sorted(batch, key=lambda point: point.x, reverse = reverse)
                # If we sort the low points, we sort by y-Axis from top to bottom
                else:
                    sorted_batch = sorted(batch, key=lambda point: point.y, reverse = True)
                
                # Assign roles, additional offset to set correct role with the help of the index
                for i, element in enumerate(sorted_batch):
                    if batch is high:
                        offset = 1
                    elif batch is mid:
                        offset = 8
                    else:
                        offset = 14
                    if len(sorted_batch) == expected_lengths[batches.index(batch)]:
                        element.role = i+offset
                    else:
                        element.role = -1 

                # Extend the sorted array
                sorted_inner_points.extend(sorted_batch)
            return sorted_inner_points
    
    def assign_roles_inside(self, inner_image, contour, pointsOfInterest, reverse):
        # This function sorts the points of interest and gives them a role
        image = inner_image.copy()
        
        #Return highest and lowest point of the contour
        highest_point = min(contour, key=lambda coord: coord[0][1])
        lowest_point = max(contour, key=lambda coord: coord[0][1])

        # Define the sizes of the rectangles, values to adjust
        upper_rect_height = 1400
        lower_rect_height = 200


        mid_rect_height = image.shape[0] - upper_rect_height - lower_rect_height

        # Define the width of the rectangles, controls right edge
        rect_width = image.shape[1]

        rect_low, rect_mid, rect_high = self.create_inner_boxes(highest_point,lowest_point,upper_rect_height,mid_rect_height,rect_width)
        high, mid, low = self.assign_inner_points_to_boxes(pointsOfInterest,rect_low,rect_mid,rect_high)
        batches = [high,mid,low]    
        
        while len(mid)>6:
            #print('First bound too high. Decreasing first bound...')
            #upper_rect_height+=10
            mid_rect_height -=10
            rect_low, rect_mid, rect_high = self.create_inner_boxes(highest_point,lowest_point,upper_rect_height,mid_rect_height,rect_width)
            high, mid, low = self.assign_inner_points_to_boxes(pointsOfInterest,rect_low,rect_mid,rect_high)
            batches = [high,mid,low]


        sorted_inner_points = self.sort_and_select_roles_inside(batches,reverse)
        return sorted_inner_points
    

        # Define two points that cross the contour twice
    def find_cutpoints(self,contour,point1,point2):
        
        point1role = point1.role
        point2role = point2.role

        # Convert pointsOfInterest to numpy arrays
        point1 = np.rint(np.array([point1.x, point1.y]))
        point2 = np.rint(np.array([point2.x, point2.y]))

        # Calculate the distance between point1 and point2
        distance = np.linalg.norm(point2 - point1)
        # Set the desired spacing between points
        spacing = 0.1 
        # Calculate the number of points needed
        num_points = int(distance / spacing)
        # Ensure a minimum number of points
        num_points = max(num_points, 2)  # At least two points
        intersection_points = []
        distance_threshold = 10.0  

        line_points = np.rint(np.linspace(point1, point2, num=num_points))
        for point in line_points:
            if abs(cv2.pointPolygonTest(contour, tuple(point), True)) < 0.1:
                # Check if the point is not too close to existing points in the array
                if all(np.linalg.norm(np.array(point) - np.array(existing_point)) > distance_threshold for existing_point in intersection_points):
                    intersection_points.append(point)

            # Break the loop once two distinct intersection points are found
            if len(intersection_points) == 2:
                break
        roles = [point1role,point2role]
        #for point in intersection_points:
        points_of_interest = []
        for i,point in enumerate(intersection_points):
            points_of_interest.append(PointOfInterest(point[0],point[1],roles[i]))
        
        return points_of_interest[0], points_of_interest[1]

    def addError(self, error):
        self.errors.append(error)
        pass

    #crop, mirror image, find points of interest for given foot give inner ones role
    def _process_foot(self,original_image, masked_images, contour, side):

        #count points from right to left
        if side == 'left':
            reverse = True
        #count points from left to right
        elif side == 'right':
            reverse = False
       
        points_of_interest = []
        inner_keypoints = []
        outer_keypoints = []
        
        
        for index, masked_image in enumerate(masked_images):
            cropped_original_image,_,_= self._crop_and_mirror(original_image, contour, self.settings.get_setting('outside')['padding'])
            cropped_masked_image, adjusted_contour, _ = self._crop_and_mirror(masked_image, contour, self.settings.get_setting('outside')['padding'])
            
            # For inner points the main issue is the area, for outer main issue is the circularity
            
            if index == 0: #index 0 contains the feet inside the contour


                try:
                    points_of_interest = self._points_of_interest(cropped_masked_image,self.settings.get_setting('inside'))
                    inner_keypoints = self.assign_roles_inside(cropped_masked_image.copy(),adjusted_contour, points_of_interest,reverse)
                except:
                    self.addError("Could not find inner keypoints for -%s- foot" % side)
            else:


                try:
                    points_of_interest = self._points_of_interest(cropped_masked_image,self.settings.get_setting('outside'))
                    outer_keypoints = self.assign_roles_outside(cropped_masked_image.copy(),adjusted_contour,points_of_interest,reverse)
                except:
                    self.addError("Could not find outer keypoints for -%s- foot" % side)

         # Join both lists together
        keypoints =  inner_keypoints+outer_keypoints
        # If only one of the two elements within a pair got found, cutpoints not possible so set both to empty poi
        
       
        # Tausche Pelottenpunkt mit den Mittelfußknochen
        # only do this if mid row has roles assigned (role with keypoint 10 found means roles have been assigned)
        if self.find_role_index(keypoints,10):
            keypoints[self.find_role_index(keypoints,10)].role = 22 #placeholder role, like temp
            keypoints[self.find_role_index(keypoints,11)].role = 10
            keypoints[self.find_role_index(keypoints,12)].role = 11
            keypoints[self.find_role_index(keypoints,13)].role = 12
            keypoints[self.find_role_index(keypoints,22)].role = 13

        return FootScannerResult(cropped_original_image, adjusted_contour, keypoints)
    # Take image, return two FootScannerResults
    def scanImage(self, imagePath, scaleFactor=False):
        original_image = cv2.imread(imagePath)

        #rescale the image to specified mmpx
        
        if not scaleFactor:
            print("scanImage - no scaleFactor")
            try:
                original_image = self.rescale_image(original_image,10) # TODO read from settings -> TARGET_DPI / 25.4
            except:
                return False
                pass
                
            
            
        else:
            print("scanImage - YES scaleFactor %s" % scaleFactor)
            # we already know the scale factor
            original_image = self.rescale_image_by_factor(original_image, scaleFactor)
            pass
        
        
        self.scaled_image = cv2.rotate(original_image, cv2.ROTATE_180)

        filtered_contours = self._filter_contours(original_image)

        #Cropping after filtering out contours
        original_image = self._crop_image(original_image)
        
        
        # Create an empty mask to store the masked image
        mask = np.zeros_like(original_image)
        # Draw the contours on the original image
        cv2.drawContours(mask, filtered_contours, -1, (255,255,255), -1)
        # Create inner and outer part
        inner_image = cv2.bitwise_and(original_image, mask)
        outer_image = cv2.bitwise_or(original_image, mask)

        #Join them into list
        masked_images = [inner_image] + [outer_image] #list of two lists

        #Apply foot processing 
        
        left =  self._process_foot(original_image,masked_images,filtered_contours[0], 'left')
        right =  self._process_foot(original_image,masked_images,filtered_contours[-1], 'right')
        #information necessary: foot-nr, foot-side
        
        return (left,right)
    
    
    def flipResultHorizontal(self,result):
        image = result.image.copy()
        flipped_image = cv2.flip(image,1)
        flipped_contour = []
        for point in result.contour:
            x, y = point[0]

            # Flip image
            x_flip = image.shape[1] - x - 1
            y_flip = y 

            # Add the transformed point to the new contour
            flipped_contour.append([[x_flip, y_flip]])
            
        # Now 'flipped_contour' is the transformed contour
        flipped_contour = np.array(flipped_contour, dtype=np.int32)
        # Flip keypoints the same way
        flipped_points_of_interest = []
        # Create flipped pointsOfInterest
        for point_of_interest in result.pointsOfInterest:
            if point_of_interest.x:
                flipped_point_of_interest = PointOfInterest(image.shape[1]-point_of_interest.x-1,
                                                            point_of_interest.y,
                                                            point_of_interest.role)
                flipped_points_of_interest.append(flipped_point_of_interest)
        # Create new FootScannerResult with flipped values
        flipped_result = FootScannerResult(flipped_image,flipped_contour,flipped_points_of_interest)
        
        return flipped_result
  
    def flipResultVertical(self,result):
        # Should flip the result horizontally and return the new FootScannerResult
        image = result.image.copy()
        flipped_image = cv2.flip(image,-1)

        flipped_contour = []
        for point in result.contour:
            x, y = point[0]

            # Flip image
            x_flip = image.shape[1] - x - 1
            y_flip = image.shape[0] - y - 1
            
            # Add the transformed point to the new contour
            flipped_contour.append([[x_flip, y_flip]])
            
        # Now 'flipped_contour' is the transformed contour
        flipped_contour = np.array(flipped_contour, dtype=np.int32)
        # Flip keypoints the same way
        flipped_points_of_interest = []
        # Create flipped pointsOfInterest
        for point_of_interest in result.pointsOfInterest:
            if point_of_interest.x:
                flipped_point_of_interest = PointOfInterest(image.shape[1]-point_of_interest.x-1,
                                                            image.shape[0]-point_of_interest.y-1,
                                                            point_of_interest.role)
                flipped_points_of_interest.append(flipped_point_of_interest)
        # Create new FootScannerResult with flipped values
        flipped_result = FootScannerResult(flipped_image,flipped_contour,flipped_points_of_interest)
        
        return flipped_result

# In[40]:


class FootScannerSettings:
    def __init__(self):
        self.settings = {}

    def add_setting(self, name, area, circularity, convexity, inertia, bgr_threshold, padding=140, blocksize=95, C=7):
        self.settings[name] = {
            # Padding increases the margin of the built bounding box of each contour
            'padding': padding,
            # Minimum size of detected blobs in _points_of_interest blob detection
            'area': area,
            #the higher the value, the more round the blobs have to be
            'circularity': circularity,
             #Higher values tend to detect full circles 
            'convexity': convexity,
            #Low inertia tends to detect ellipses
            'inertia': inertia,
            # neighbor pixels considered when calculating the in adaptive threshold. Has to be odd.
            'blocksize': blocksize,
            #constant which gets subtracted to mean in adaptive threshold
            'C': C,
            # threshold that sets pixels on the original image to white if they are above a certain value (e.g., too red)
            'bgr_threshold': bgr_threshold
        }

    def get_setting(self, name):
        return self.settings.get(name, None)

    
    def __str__(self):
        # Return a string representation of the settings
        settings_str = "{\n"
        for setting, value in self.settings.items():
            settings_str += f"    '{setting}': {value},\n"
        settings_str += "}"
        return settings_str

# In[118]:



#############################



 
# Call scanImage and flipResult
#(result_left, result_right) = foot_scanner.scanImage('feetsies/feet-7.jpg')

#result_right = foot_scanner.flipResult(result_right,right = True)
#footscanner before flipping

#if feet are scanned like in 7 and 8, horizonal flip on right is sufficient, else
#result_right = foot_scanner.flipResultVertical(result_right)
#result_left = foot_scanner.flipResultHorizontal(foot_scanner.flipResultVertical(result_left))
#else



# In[126]:

from ..models import FoamPrintPoint
from dataInspection.helpers.pois import FOAM_POINT_CHOICES, FoamPointDefinitions

#result_left.draw_point_of_interest(12)

def store_poi(foam_instance, poi, to_left = False):
    foot = FoamPrintPoint.RIGHT
    if to_left:
        foot = FoamPrintPoint.LEFT
    
    try:
        if poi.role != FoamPointDefinitions.UNRECOGNIZED:
            fp = FoamPrintPoint.objects.create(foamPrintAnalysis=foam_instance, x=poi.x,y=poi.y,pointType=poi.role, foot=foot)
        else:
            print("No recognized role")
            fp = FoamPrintPoint.objects.create(foamPrintAnalysis=foam_instance, x=poi.x,y=poi.y,pointType=poi.role, foot=foot)
        
        
            
    except:
        print("Could not save point %s, %s" % (foam_instance, poi))
    pass





def store_result_to_model(result, instance, to_left = False):
    _, buffer = cv2.imencode('.jpg', result.image) 
    image_bytes = buffer.tobytes()
    content_file = ContentFile(image_bytes)
    django_file = File(content_file)

    print(result)

    if to_left:
        if instance.leftFoot:
            # If it does, delete the existing file
            instance.leftFoot.delete()

        instance.points.filter(foot=FoamPrintPoint.LEFT).delete()

        instance.leftFoot.save('%s_left.jpg' % instance.id, django_file)

        

        for poi in result.pointsOfInterest:
            store_poi(instance, poi, to_left)

        # delete all  

    if not to_left:
        if instance.rightFoot:
            # If it does, delete the existing file
            instance.rightFoot.delete()

        instance.rightFoot.save('%s_right.jpg' % instance.id, django_file)

        instance.points.filter(foot=FoamPrintPoint.RIGHT).delete()

        for poi in result.pointsOfInterest:
            store_poi(instance, poi, to_left)


    instance.save()

