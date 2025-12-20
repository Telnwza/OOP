class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        result = []
        lenght = len(nums)
        for i in range(lenght):
            for j in range(i+1, lenght):
                if nums[i] + nums[j] == target:
                  result = [i, j]
        return result
    
print(Solution().twoSum([3,3], 6))