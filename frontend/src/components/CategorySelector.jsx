import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Circle, Plus } from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { useToast } from "@/hooks/use-toast";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
const CategorySelector = ({ categories, categoryId, onCategoryChange }) => {
  const [showNewForm, setShowNewForm] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [selectedColor, setSelectedColor] = useState("#EF9C66");
  const { getToken } = useAuth();
  const { toast } = useToast();

  const COLORS = [
    "#EF9C66",
    "#FCDC94",
    "#C8CFA0",
    "#78ABA8",
    "#FF9E9E",
    "#C0ACD0",
  ];

  const handleAddCategory = async (e) => {
    e.preventDefault();
    if (!newCategoryName.trim()) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/categories/`,
        {
          method: "POST",
          headers: {
            Authorization: `Token ${getToken()}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: newCategoryName.trim(),
            color: selectedColor,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to create category");

      const newCategory = await response.json();
      toast({ title: "Category created successfully" });

      // Reset form
      setNewCategoryName("");
      setShowNewForm(false);

      // Select the new category
      onCategoryChange(newCategory.id);
    } catch (error) {
      toast({ title: "Failed to create category", variant: "destructive" });
    }
  };

  return (
    <Select value={categoryId} onValueChange={onCategoryChange}>
      <SelectTrigger className="w-[240px] h-10 rounded-md border border-[#957139]">
        <SelectValue placeholder="Select Category" />
      </SelectTrigger>

      <SelectContent>
        {categories.map((category) => (
          <SelectItem key={category.id} value={category.id}>
            <div className="flex items-center">
              <Circle
                className="w-4 h-4 mr-2"
                fill={category.color}
                strokeWidth={0}
              />
              {category.name}
            </div>
          </SelectItem>
        ))}

        {/* Divider & "Add Category" item at the bottom */}
        <div className="px-2 py-1.5 border-t border-[#95714f]/20 mt-1">
          <Dialog>
            <DialogTrigger asChild>
              <button
                type="button"
                className="flex items-center w-full text-sm text-[#95714f] hover:text-[#7a5e41] px-2 py-1 rounded-md hover:bg-[#95714f]/10"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Category
              </button>
            </DialogTrigger>

            <DialogContent className="bg-[#FAF1E3] text-white">
              <DialogHeader>
                <DialogTitle className="text-black/80">
                  Create a New Category
                </DialogTitle>
                <DialogDescription className="text-black/80">
                  Give your category a name and select a color.
                </DialogDescription>
              </DialogHeader>

              <form onSubmit={handleAddCategory}>
                <div className="space-y-3 py-2">
                  <Input
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                    placeholder="Category name"
                    className="border-white/70 placeholder-white/40 text-black"
                    autoFocus
                  />

                  <div className="flex">
                    {COLORS.map((color) => {
                      const isSelected = selectedColor === color;
                      return (
                        <div key={color} className="flex-1 flex justify-center">
                          <button
                            type="button"
                            onClick={() => setSelectedColor(color)}
                            className={`w-6 h-6 rounded-full transition-all ${
                              isSelected
                                ? "ring-2 ring-white ring-offset-2 ring-offset-[#95714f]"
                                : ""
                            }`}
                            style={{ backgroundColor: color }}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>

                <DialogFooter>
                  {/* Remove the Cancel button, keep only Create */}
                  <Button
                    type="submit"
                    className="bg-[#95714f] text-white hover:bg-white/90"
                  >
                    Create Category
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </SelectContent>
    </Select>
  );
};

export default CategorySelector;
