# Smart Packing
Create optimized pallets or parcels for a list of items to pack for shipping quotes.
Each item has the following attributes:
- weight
- length
- width
- height
- assembled (boolean)
- bundled (boolean)

Each pallet has the following attributes:
- Maximum height (max_height)
- Fixed length (length)
- Fixed width (width)
- Weight (weight)
- Type (BD, PLT4, PLT6, PLT8) - `BD means BUNDLE`


## Algorithm
Generate the minimum number of pallets using a linear approach, resulting in a sub-optimal solution.
### Constraints
1. Assembled items cannot be stacked on top of another assembled item in the same pallet.
2. Each bundled item must be in a separate bundle and cannot share a pallet with other items.
3. Smaller pallets are preferred but not required.
4. No constraints on the weight of a pallet.

